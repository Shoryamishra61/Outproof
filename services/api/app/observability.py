"""Manual technical telemetry; private requests and provider payloads never enter events."""

import os

import sentry_sdk


def technical_event(event: dict, hint: dict) -> dict:
    retained = {
        key: event[key]
        for key in (
            "event_id",
            "timestamp",
            "start_timestamp",
            "type",
            "transaction",
            "transaction_info",
            "platform",
            "release",
            "environment",
            "level",
            "message",
            "logger",
        )
        if key in event
    }
    trace = event.get("contexts", {}).get("trace", {})
    retained["contexts"] = {
        "trace": {
            key: trace[key]
            for key in (
                "trace_id",
                "span_id",
                "parent_span_id",
                "op",
                "status",
                "origin",
            )
            if key in trace
        }
    }
    retained["spans"] = [
        {
            key: span[key]
            for key in (
                "trace_id",
                "span_id",
                "parent_span_id",
                "op",
                "status",
                "timestamp",
                "start_timestamp",
            )
            if key in span
        }
        for span in event.get("spans", [])
    ]
    return retained


def configure() -> bool:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return False
    sentry_sdk.init(
        dsn=dsn,
        default_integrations=False,
        auto_enabling_integrations=False,
        send_default_pii=False,
        max_request_body_size="never",
        traces_sample_rate=0.1,
        profiles_sample_rate=0,
        release=os.getenv("RENDER_GIT_COMMIT", "local"),
        environment=os.getenv("GROUND_RULE_ENV", "development"),
        before_send=technical_event,
        before_send_transaction=technical_event,
    )
    return True
