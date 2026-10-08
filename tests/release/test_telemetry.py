import json

from app.observability import technical_event


def test_telemetry_drops_private_context_and_retains_diagnostic_timing():
    event = {
        "type": "transaction",
        "transaction": "ground_rule.compile",
        "timestamp": 4,
        "request": {"data": "PRIVATE PROMPT", "headers": {"Authorization": "SECRET"}},
        "user": {"ip_address": "PRIVATE"},
        "breadcrumbs": ["SECRET"],
        "contexts": {
            "trace": {
                "trace_id": "trace",
                "span_id": "span",
                "op": "compile",
                "data": {"gps": "PRIVATE"},
            }
        },
        "spans": [
            {
                "op": "ground_rule.gemma_rank",
                "timestamp": 4,
                "start_timestamp": 1,
                "description": "SECRET",
                "data": {"prompt": "PRIVATE"},
            }
        ],
        "exception": {"values": [{"value": "SECRET"}]},
    }
    result = technical_event(event, {})
    serialized = json.dumps(result)
    assert "PRIVATE" not in serialized and "SECRET" not in serialized
    assert result["spans"] == [
        {"op": "ground_rule.gemma_rank", "timestamp": 4, "start_timestamp": 1}
    ]
    assert result["contexts"]["trace"]["trace_id"] == "trace"
