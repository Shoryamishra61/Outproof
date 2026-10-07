"""Evaluate synthetic structural contracts, not parser or outing correctness."""

import json
from pathlib import Path

from ground_rule.models import CONTRACT_MODELS
from pydantic import BaseModel, ConfigDict, JsonValue, StrictBool, StrictStr, ValidationError


class ContractCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: StrictStr
    synthetic: StrictBool
    model: StrictStr
    payload: JsonValue
    expected_valid: StrictBool


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    models = {model.__name__: model for model in CONTRACT_MODELS}
    results: list[dict[str, str | bool]] = []
    for line in (root / "evals/cases/contracts.jsonl").read_text(encoding="utf-8").splitlines():
        case = ContractCase.model_validate_json(line)
        if not case.synthetic:
            raise ValueError("Contract evaluation requires explicitly synthetic cases")
        try:
            models[case.model].model_validate_json(json.dumps(case.payload))
            valid = True
        except ValidationError:
            valid = False
        results.append({"id": case.id, "passed": valid == case.expected_valid})
    if not results or len({result["id"] for result in results}) != len(results):
        raise ValueError("Contract cases must be nonempty and have unique IDs")
    failures = [result["id"] for result in results if not result["passed"]]
    report = {
        "scope": "synthetic structural contracts only",
        "cases": len(results),
        "passed": len(results) - len(failures),
        "failed": failures,
        "results": results,
    }
    (root / "evals/reports/contracts.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in report.items() if key != "results"}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
