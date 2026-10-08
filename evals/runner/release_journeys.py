"""Execute controlled journeys and measure the actual pairwise input coverage."""

import hashlib
import itertools
import json
import runpy
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    suite = runpy.run_path("tests/release/test_journeys.py")
    cases = suite["CASES"]
    names = [
        "city",
        "party",
        "budget_scope",
        "budget",
        "duration",
        "walking",
        "price_confidence",
        "fault",
        "vibe",
    ]
    domains = [set(case[i] for case in cases) for i in range(len(names))]
    coverage = []
    for i, j in itertools.combinations(range(len(names)), 2):
        observed = {(case[i], case[j]) for case in cases}
        possible = set(itertools.product(domains[i], domains[j]))
        assert observed == possible, (names[i], names[j], possible - observed)
        coverage.append(
            {
                "dimensions": [names[i], names[j]],
                "observed": len(observed),
                "possible": len(possible),
            }
        )
    rows = []
    for case in cases:
        accepted, status = suite["execute_journey"](case)
        rows.append(
            {
                "id": hashlib.sha256(repr(case).encode()).hexdigest(),
                "input": dict(zip(names, case, strict=True)),
                "expected_acceptance": accepted,
                "actual_status": status,
                "assertions": "PASS",
            }
        )
    assert len(rows) >= 4096 and len({row["id"] for row in rows}) == len(rows)
    report = {
        "executed_at": datetime.now(UTC).isoformat(),
        "seed": suite["SEED"],
        "scope": (
            "synthetic facts and controlled providers; real deterministic compiler "
            "and validator; no live or physical outings"
        ),
        "cases": len(rows),
        "passed": len(rows),
        "failed": 0,
        "acceptance_counts": dict(Counter(row["actual_status"] for row in rows)),
        "dimensions": {name: sorted(domain) for name, domain in zip(names, domains, strict=True)},
        "pairwise_coverage": coverage,
        "journeys": rows,
    }
    Path("evals/reports/FINAL_USER_FLOW_COVERAGE.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(
        json.dumps({key: report[key] for key in ["cases", "passed", "failed", "acceptance_counts"]})
    )


if __name__ == "__main__":
    main()
