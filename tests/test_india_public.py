from datetime import UTC, datetime

from evals.runner.india_public import cases, classify, controls_for


def test_india_cases_are_distinct_and_use_real_search_not_invented_coordinates():
    inputs = cases()
    assert len(inputs) == len({c["id"] for c in inputs}) == len({c["query"] for c in inputs}) == 100
    assert all("origin" not in case for case in inputs)


def test_refusal_and_outage_are_never_counted_as_accepted_plans():
    controls = controls_for({"latitude": 13.0, "longitude": 80.0}, datetime.now(UTC))
    assert (
        classify(
            409,
            {"status": "FAILURE", "code": "NO_GROUNDED_CANDIDATES", "message": "Missing facts"},
            controls,
        )
        == "TYPED_REJECTION"
    )
    assert (
        classify(
            503,
            {
                "status": "FAILURE",
                "code": "SOURCE_TEMPORARILY_UNAVAILABLE",
                "message": "Unavailable",
            },
            controls,
        )
        == "TEMPORARY_PROVIDER_ERROR"
    )
