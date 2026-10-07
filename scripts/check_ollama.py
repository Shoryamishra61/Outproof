"""Verify one synthetic structured-output call; this is not a parser benchmark."""

import json
import os
from pathlib import Path
from time import perf_counter

import httpx
from jsonschema import Draft202012Validator


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    schema = json.loads((root / "contracts/constraint-set.schema.json").read_text())
    # The bootstrap echo requires every optional key, including explicit nulls.
    schema["required"] = list(schema["properties"])
    model = os.getenv("GEMMA_MODEL", "gemma4:e4b")
    controls = {
        "currency_code": "INR",
        "budget_minor_units": 50000,
        "budget_scope": "PER_PERSON",
        "duration_max_minutes": 90,
        "party_mode": "FRIEND",
        "party_size": 2,
        "vibes": ["Talk"],
        "hard_constraints": [{"kind": "EXCLUDE_CATEGORY", "value": "mall"}],
        "soft_constraints": [{"preference": "quiet"}],
        "max_walking_minutes": 20,
        "max_walking_meters": 2500.0,
        "return_by_local": None,
        "locale": "en-IN",
        "origin": None,
        "departure_at": None,
        "strict_budget": True,
    }
    # Structured controls are authoritative; this echo is not free-text interpretation.
    locked_controls = (
        "currency_code",
        "budget_minor_units",
        "budget_scope",
        "duration_max_minutes",
        "party_size",
        "max_walking_minutes",
        "max_walking_meters",
        "return_by_local",
        "departure_at",
        "origin",
    )
    for name in locked_controls:
        schema["properties"][name]["const"] = controls[name]
    started = perf_counter()
    with httpx.Client(timeout=180, trust_env=False) as client:
        response = client.post(
            os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/chat",
            json={
                "model": model,
                "stream": False,
                "think": False,
                "format": schema,
                "messages": [
                    {
                        "role": "user",
                        "content": "Return these synthetic controls unchanged as JSON: "
                        + json.dumps(controls)
                        + "\nSchema: "
                        + json.dumps(schema),
                    }
                ],
                "options": {"temperature": 0, "num_predict": 1024, "num_ctx": 4096},
            },
        )
        response.raise_for_status()
        payload = response.json()
    if payload.get("done") is not True:
        raise ValueError("Ollama returned an incomplete response")
    parsed = json.loads(payload["message"]["content"])
    Draft202012Validator(schema).validate(parsed)
    if parsed != controls:
        print(json.dumps({"expected_synthetic_controls": controls, "actual": parsed}))
        raise ValueError("Model changed the synthetic controls")
    report = {
        "status": "PASS",
        "synthetic": True,
        "model": model,
        "schema_valid": True,
        "controls_preserved": True,
        "locked_structured_controls": locked_controls,
        "call_latency_ms": round((perf_counter() - started) * 1000),
        "output": parsed,
    }
    (root / "evals/reports/bootstrap-model.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in report.items() if key != "output"}))


if __name__ == "__main__":
    main()
