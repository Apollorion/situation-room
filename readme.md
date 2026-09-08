# The Situation Room

This is a down and dirty python app that will notify users of nhl situation room updates.

[https://situationroom.apollorion.com](https://situationroom.apollorion.com)

## Telemetry

Flask and requests use the upstream OpenTelemetry instrumentors.
Set `OTEL_EXPORTER_OTLP_ENDPOINT` and `OTEL_EXPORTER_OTLP_PROTOCOL` (`grpc` or `http/protobuf`) for production traces.
Structured stdout logs include trace and span identifiers; the runtime collector forwards them to Grafana.
Trace export preserves HTTP status, safe operation counts, and exception types while excluding private URLs, recipient keys, provider response bodies, and exception text.
Handled scraper errors mark the batch span as failed; provider rejection stops notification processing before the cursor advances.
Notification retries can repeat a previously successful recipient after another recipient fails, because Pushover does not provide an application idempotency key here.
Python's SDK shutdown hook flushes normal process exits, and SIGTERM takes that exit path; abrupt process or host loss can still discard buffered telemetry.

Run the telemetry regressions with `uv run --with-requirements requirements.txt --with pytest python -m pytest -q`.
CI runs these tests before publishing the container under its immutable Git SHA tag, with provenance and an SBOM.
Deployment consumes that image through the current GitOps configuration; the build does not write into a separate infrastructure repository.
