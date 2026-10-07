"""Evaluate supplied fictional facts against deterministic policy, without I/O."""

import json
from datetime import datetime
from pathlib import Path

from ground_rule.models import CandidatePlan, ConstraintSet
from ground_rule.policy import validate_plan
from pydantic import ValidationError

from evals.cases.policy import NOW, policy_cases


def run_cases() -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for case in policy_cases():
        if case["synthetic"] is not True:
            raise ValueError("Only synthetic policy cases are allowed")
        try:
            plan = CandidatePlan.model_validate(case["plan"])
        except ValidationError:
            accepted = False
            failed_codes = ["STRUCTURE"]
        else:
            result = validate_plan(
                plan,
                ConstraintSet.model_validate(case["constraints"]),
                as_of=datetime.fromisoformat(case["as_of"]) if "as_of" in case else NOW,
                allow_fixture=True,
            )
            accepted = result.accepted
            failed_codes = [check.code.value for check in result.checks if check.status != "PASS"]
        passed = accepted == case["accepted"] and (
            case["failure"] is None or case["failure"] in failed_codes
        )
        results.append(
            {
                "id": case["id"],
                "expected_accepted": case["accepted"],
                "accepted": accepted,
                "failed_codes": failed_codes,
                "passed": passed,
            }
        )
    if not results or len({item["id"] for item in results}) != len(results):
        raise ValueError("Policy cases must be nonempty and uniquely identified")
    return results


def main() -> None:
    results = run_cases()
    failures = [row["id"] for row in results if not row["passed"]]
    report = {
        "scope": "synthetic deterministic policy fixtures; zero real outings",
        "cases": len(results),
        "passed": len(results) - len(failures),
        "failed": failures,
        "results": results,
    }
    root = Path(__file__).resolve().parents[2]
    (root / "evals/reports/policy.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in report.items() if key != "results"}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
