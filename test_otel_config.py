import io
import json
import logging
from unittest.mock import Mock

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

import otel_config


def test_error_status_and_correlation_survive_privacy_filter():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(otel_config.SafeSpanExporter(exporter)))
    output = io.StringIO()
    handler = logging.StreamHandler(output)
    handler.setFormatter(otel_config.SafeJSONFormatter())
    logger = otel_config.logger
    old_handlers, old_level, old_propagate = logger.handlers, logger.level, logger.propagate
    logger.handlers, logger.level, logger.propagate = [handler], logging.INFO, False
    try:
        with provider.get_tracer("synthetic").start_as_current_span("synthetic.failure") as span:
            span.set_attribute("http.url", "https://example.test/private?token=private")
            span.set_attribute("notification.group", "private")
            span.set_attribute("http.status_code", 503)
            error = RuntimeError("private provider payload")
            span.record_exception(error)
            otel_config.record_failure(span, error)
    finally:
        logger.handlers, logger.level, logger.propagate = old_handlers, old_level, old_propagate
        provider.shutdown()
    finished = exporter.get_finished_spans()[0]
    assert finished.status.status_code == StatusCode.ERROR
    assert finished.attributes["http.status_code"] == 503
    assert "private" not in str(finished.attributes)
    assert "private" not in str(finished.events)
    assert not finished.status.description
    record = json.loads(output.getvalue())
    assert record["trace_id"] == format(finished.context.trace_id, "032x")
    assert record["span_id"] == format(finished.context.span_id, "016x")
    assert record["error_type"] == "RuntimeError"
    assert "private" not in output.getvalue()


def test_provider_rejection_is_not_reported_as_success():
    response = Mock()
    response.json.return_value = {"status": 0, "errors": ["private provider payload"]}
    with pytest.raises(RuntimeError, match="provider rejected"):
        otel_config.require_success(response)
    response.raise_for_status.assert_called_once()


def test_library_errors_do_not_leak_urls_or_exception_text():
    record = logging.LogRecord("werkzeug", logging.ERROR, __file__, 1, "private URL", (), (ValueError, ValueError("private"), None))
    result = json.loads(otel_config.SafeJSONFormatter().format(record))
    assert result["error_type"] == "ValueError"
    assert "private" not in str(result)
