import os

import requests
from opentelemetry.instrumentation.requests import RequestsInstrumentor

import helpers
import otel_config

# Initialize OpenTelemetry
tracer = otel_config.init_telemetry("situation-room-notifier", "1.0.0")

# Instrument requests library for automatic HTTP tracing
# Exclude OTEL collector endpoints to prevent instrumentation loops
RequestsInstrumentor().instrument(
    excluded_urls=".*v1/traces.*,.*opentelemetry-collector.*"
)

groups = helpers.get_groups()
posts = helpers.get_posts()
last_update = helpers.get_last_update()

def update_message(post, key, title, _message):
    if post[key] is not None:
        _message += f"<b>{title}</b>: {post[key]}\n"
    return _message

with tracer.start_as_current_span("notifier.process_posts") as root_span:
    root_span.set_attribute("notifier.total_posts", len(posts))
    root_span.set_attribute("notifier.last_update", last_update)
    notifications_sent = 0

    for post in posts:
        if last_update == "NEVER_UPDATED":
            otel_config.logger.info("notification cursor not initialized")
            break

        if post["url"] == last_update:
            otel_config.logger.info("notification cursor reached")
            break

        with tracer.start_as_current_span("notifier.process_post") as post_span:
            post_span.set_attribute("post.url", post["url"])
            post_span.set_attribute("post.type", post["type"])

            home = post["home"]
            away = post["away"]

            otel_config.logger.info("processing notification")
            post_span.set_attribute("post.home_team", home)
            post_span.set_attribute("post.away_team", away)

            notification_groups = [groups[helpers.group_to_team[home]], groups[helpers.group_to_team[away]]]

            otel_config.logger.info("notification groups selected", extra={"count": len(notification_groups)})

            title = f"{home} vs {away}: {post['type']}"

            message = update_message(post, "short_description", "Desc", "")
            message = update_message(post, "challenge_initiator", "Initiated By", message)
            message = update_message(post, "type_of_challenge", "Challenge Type", message)
            message = update_message(post, "result", "Result", message)
            message = update_message(post, "explanation", "Explanation", message)
            message = update_message(post, "penalty", "Penalty", message)

            for group in notification_groups:
                with tracer.start_as_current_span("notifier.send_notification") as notify_span:

                    otel_config.logger.info("sending notification")
                    r = requests.post("https://api.pushover.net/1/messages.json", data={
                        "token": os.environ["PUSHOVER_APPLICATION_TOKEN"],
                        "user": group,
                        "title": title,
                        "message": message,
                        "ttl": 86400,
                        "html": 1
                    }, timeout=30)
                    notify_span.set_attribute("http.status_code", r.status_code)
                    otel_config.require_success(r)
                    notifications_sent += 1

                    otel_config.logger.info("notification delivered")

    root_span.set_attribute("notifier.notifications_sent", notifications_sent)

helpers.write_last_update(posts[0]["url"])
otel_config.logger.info("notification job completed")
