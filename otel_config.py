import json
import logging
import os
import signal
import sys

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter as GRPCExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Event, ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger("situation-room")
SAFE_ATTRIBUTES = {
    "http.route", "http.request.method", "http.method", "http.response.status_code",
    "http.status_code", "network.protocol.version", "error.type",
    "scraper.posts_found", "scraper.new_posts", "notifier.total_posts",
    "notifier.notifications_sent", "http.response_size", "file.size_bytes",
}


class SafeSpanExporter(SpanExporter):
    def __init__(self, exporter):
        self.exporter = exporter

    def export(self, spans):
        safe = []
        for span in spans:
            events = [
                Event("exception", attributes={"exception.type": event.attributes["exception.type"]}, timestamp=event.timestamp)
                for event in span.events
                if event.name == "exception" and "exception.type" in event.attributes
            ]
            safe.append(ReadableSpan(
                name=span.name, context=span.context, parent=span.parent,
                resource=span.resource, kind=span.kind,
                attributes={key: value for key, value in span.attributes.items() if key in SAFE_ATTRIBUTES},
                events=events, links=(), status=Status(span.status.status_code),
                start_time=span.start_time, end_time=span.end_time,
                instrumentation_scope=span.instrumentation_scope,
            ))
        return self.exporter.export(safe)

    def shutdown(self):
        self.exporter.shutdown()

    def force_flush(self, timeout_millis=30000):
        return self.exporter.force_flush(timeout_millis)


class SafeJSONFormatter(logging.Formatter):
    def format(self, record):
        payload = {"level": record.levelname, "service": "situation-room"}
        payload["message"] = record.getMessage() if record.name == "situation-room" else "library event"
        if record.exc_info and record.exc_info[0]:
            payload["error_type"] = record.exc_info[0].__name__
        for field in ("error_type", "status_code", "count"):
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        context = trace.get_current_span().get_span_context()
        if context.is_valid:
            payload["trace_id"] = format(context.trace_id, "032x")
            payload["span_id"] = format(context.span_id, "016x")
        return json.dumps(payload)


def init_telemetry(service_name, service_version="1.0.0"):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(SafeJSONFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
    sys.excepthook = lambda kind, value, traceback: logger.error("process failed", exc_info=(kind, value, traceback))
    signal.signal(signal.SIGTERM, lambda _signal, _frame: sys.exit(0))
    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("SERVICE_VERSION", service_version),
        "deployment.environment.name": os.getenv("ENVIRONMENT", "development"),
    })
    provider = TracerProvider(resource=resource)
    if os.getenv("OTEL_TRACES_ENABLED", "true").lower() == "true":
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
        protocol = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf").lower()
        try:
            if protocol in ("http", "http/protobuf"):
                endpoint = endpoint.rstrip("/")
                if not endpoint.endswith("/v1/traces"):
                    endpoint += "/v1/traces"
                exporter = HTTPExporter(endpoint=endpoint, timeout=5)
            elif protocol == "grpc":
                exporter = GRPCExporter(endpoint=endpoint, timeout=5)
            else:
                raise ValueError("unsupported telemetry protocol")
            provider.add_span_processor(BatchSpanProcessor(SafeSpanExporter(exporter)))
        except Exception:
            logger.exception("telemetry initialization failed")
            raise
    trace.set_tracer_provider(provider)
    logger.info("telemetry initialized")
    return trace.get_tracer(service_name)


def get_tracer(name):
    return trace.get_tracer(name)


def record_failure(span, error):
    span.set_status(Status(StatusCode.ERROR))
    span.set_attribute("error.type", type(error).__name__)
    span.add_event("exception", {"exception.type": type(error).__name__})
    logger.error("operation failed", extra={"error_type": type(error).__name__})


def require_success(response):
    response.raise_for_status()
    if response.json().get("status") != 1:
        raise RuntimeError("notification provider rejected operation")
