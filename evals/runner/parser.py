"""Explicit real local-model benchmark; never part of offline CI or policy validation."""

import argparse
import hashlib
import json
import statistics
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx
from app.parser import ParserAdditions, model_request, parse_output
from ground_rule.models import ConstraintSet
from pydantic import ValidationError

from evals.cases.parser import parser_cases


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise ValueError("Refusing to overwrite a preserved benchmark; choose a new output")
    root = Path(__file__).resolve().parents[2]
    rows: list[dict[str, object]] = []
    cases = parser_cases()
    with httpx.Client(timeout=120, trust_env=False) as client:
        tags = client.get("http://127.0.0.1:11434/api/tags")
        tags.raise_for_status()
        installed = next(model for model in tags.json()["models"] if model["name"] == args.model)
        for case in cases:
            controls = ConstraintSet.model_validate(case["controls"])
            started = perf_counter()
            raw = ""
            error = None
            content: dict = {}
            parsed = None
            try:
                response = client.post(
                    "http://127.0.0.1:11434/api/chat",
                    json=model_request(controls, case["text"], args.model),
                )
                response.raise_for_status()
                payload = response.json()
                if payload.get("done") is not True:
                    raise ValueError("Incomplete model response")
                raw = payload["message"]["content"]
                decoded = json.loads(raw)
                if isinstance(decoded, dict):
                    content = decoded
                parsed = ParserAdditions.model_validate_json(raw)
                content = parsed.model_dump(mode="json")
            except (httpx.HTTPError, ValueError, KeyError, TypeError, ValidationError) as exc:
                error = type(exc).__name__
            merged = parse_output(raw, controls, case["text"])
            expected = case["expected"]
            exact_fields = {}
            for field in ParserAdditions.model_fields:
                value = content.get(field)
                wanted = expected[field]
                if isinstance(wanted, list):
                    exact_fields[field] = isinstance(value, list) and set(value) == set(wanted)
                elif field == "return_by_local" and wanted:
                    try:
                        exact_fields[field] = datetime.fromisoformat(
                            value
                        ) == datetime.fromisoformat(wanted)
                    except (TypeError, ValueError):
                        exact_fields[field] = False
                else:
                    exact_fields[field] = value == wanted and field in content
            authoritative = [
                key
                for key, value in controls.model_dump().items()
                if key not in {"hard_constraints", "soft_constraints"} and value is not None
            ]
            returned = isinstance(merged, ConstraintSet)
            preserved = returned and all(
                getattr(controls, key) == getattr(merged, key) for key in authoritative
            )
            raw_fields = json.loads(raw) if parsed is not None else content
            extra = [key for key in raw_fields if key not in ParserAdditions.model_fields]
            place_fields = [
                key
                for key in content
                if any(
                    word in key.casefold()
                    for word in ("place", "venue", "restaurant", "coordinate", "route")
                )
            ]
            wanted_unsupported = set(expected["unsupported"])
            retained = returned and wanted_unsupported.issubset(
                {item.value for item in merged.hard_constraints if item.kind == "UNSUPPORTED"}
            )
            rows.append(
                {
                    "id": case["id"],
                    "group": case["group"],
                    "schema_valid": parsed is not None,
                    "latency_ms": round((perf_counter() - started) * 1000),
                    "raw_output": raw,
                    "error": error,
                    "exact_fields": exact_fields,
                    "returned_constraint_set": returned,
                    "controls_preserved": preserved,
                    "currency_preserved": returned
                    and controls.currency_code == merged.currency_code,
                    "numeric_preserved": returned
                    and all(
                        getattr(controls, key) == getattr(merged, key)
                        for key in ("budget_minor_units", "duration_max_minutes", "party_size")
                    ),
                    "corrupted_controls": returned and not preserved,
                    "raw_unsupported_retained": isinstance(content.get("unsupported"), list)
                    and wanted_unsupported.issubset(content["unsupported"]),
                    "unsupported_retained": retained,
                    "unsupported_failure_retained": bool(wanted_unsupported)
                    and not returned
                    and all(value in merged.message for value in wanted_unsupported),
                    "unsupported_case": bool(wanted_unsupported),
                    "invented_fields": extra,
                    "hallucinated_place_fields": place_fields,
                    "output": merged.model_dump(mode="json"),
                }
            )
            if len(rows) % 10 == 0:
                print(
                    json.dumps(
                        {
                            "completed": len(rows),
                            "schema_valid": sum(row["schema_valid"] for row in rows),
                        }
                    ),
                    flush=True,
                )
    unsupported = [row for row in rows if row["unsupported_case"]]
    metrics = {
        "schema_valid": sum(row["schema_valid"] for row in rows),
        "returned_constraint_sets": sum(row["returned_constraint_set"] for row in rows),
        "controls_preserved": sum(row["controls_preserved"] for row in rows),
        "authoritative_control_corruptions": sum(row["corrupted_controls"] for row in rows),
        "currency_preserved": sum(row["currency_preserved"] for row in rows),
        "numeric_preserved": sum(row["numeric_preserved"] for row in rows),
        "hard_soft_exact": sum(
            all(
                row["exact_fields"][key]
                for key in ("exclusions", "dietary", "unsupported", "preferences")
            )
            for row in rows
        ),
        "exclusions_exact": sum(row["exact_fields"]["exclusions"] for row in rows),
        "dietary_exact": sum(row["exact_fields"]["dietary"] for row in rows),
        "preferences_exact": sum(row["exact_fields"]["preferences"] for row in rows),
        "unsupported_raw_retained": sum(row["raw_unsupported_retained"] for row in unsupported),
        "unsupported_merged_retained": sum(row["unsupported_retained"] for row in unsupported),
        "unsupported_failure_retained": sum(
            row["unsupported_failure_retained"] for row in unsupported
        ),
        "unsupported_cases": len(unsupported),
        "hallucinated_place_count": sum(len(row["hallucinated_place_fields"]) for row in rows),
        "invented_field_count": sum(len(row["invented_fields"]) for row in rows),
        "all_additions_exact": sum(all(row["exact_fields"].values()) for row in rows),
        "median_parser_call_ms": round(statistics.median(row["latency_ms"] for row in rows)),
    }
    report = {
        "scope": "100 synthetic free-text cases, real local Gemma; zero real outings",
        "executed_at": datetime.now(UTC).isoformat(),
        "model": installed,
        "cases": len(rows),
        "prompt_sha256": hashlib.sha256((root / "prompts/parser.md").read_bytes()).hexdigest(),
        "case_sha256": hashlib.sha256((root / "evals/cases/parser.py").read_bytes()).hexdigest(),
        "adapter_sha256": hashlib.sha256(
            (root / "services/api/app/parser.py").read_bytes()
        ).hexdigest(),
        "settings": {"temperature": 0, "seed": 42, "num_ctx": 4096, "num_predict": 384},
        "metrics": metrics,
        "results": rows,
    }
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(metrics), flush=True)


if __name__ == "__main__":
    main()
