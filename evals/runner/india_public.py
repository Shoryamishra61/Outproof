"""Resumable, paced India journeys against the actual public API; never simulated outings."""

import argparse
import asyncio
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo

import httpx
from ground_rule.models import CompilationFailure, CompiledPlan, ConstraintSet
from ground_rule.policy import validate_plan

API = "https://outproof-api.onrender.com"
CITIES = (
    "Chennai",
    "Mumbai",
    "New Delhi",
    "Bengaluru",
    "Hyderabad",
    "Kolkata",
    "Pune",
    "Ahmedabad",
    "Jaipur",
    "Chandigarh",
    "Kochi",
    "Coimbatore",
    "Madurai",
    "Tiruchirappalli",
    "Salem",
    "Tirunelveli",
    "Vellore",
    "Thanjavur",
    "Erode",
    "Tiruppur",
    "Puducherry",
    "Thiruvananthapuram",
    "Kozhikode",
    "Thrissur",
    "Kollam",
    "Alappuzha",
    "Kottayam",
    "Palakkad",
    "Kannur",
    "Mysuru",
    "Mangaluru",
    "Hubballi",
    "Belagavi",
    "Davanagere",
    "Shivamogga",
    "Udupi",
    "Tumakuru",
    "Ballari",
    "Vijayawada",
    "Visakhapatnam",
    "Guntur",
    "Tirupati",
    "Kurnool",
    "Nellore",
    "Rajamahendravaram",
    "Warangal",
    "Karimnagar",
    "Nizamabad",
    "Khammam",
    "Nagpur",
    "Nashik",
    "Kolhapur",
    "Chhatrapati Sambhajinagar",
    "Solapur",
    "Amravati",
    "Satara",
    "Panaji",
    "Margao",
    "Surat",
    "Vadodara",
    "Rajkot",
    "Bhavnagar",
    "Jamnagar",
    "Gandhinagar",
    "Udaipur",
    "Jodhpur",
    "Ajmer",
    "Bikaner",
    "Kota",
    "Alwar",
    "Indore",
    "Bhopal",
    "Gwalior",
    "Jabalpur",
    "Ujjain",
    "Raipur",
    "Bilaspur Chhattisgarh",
    "Lucknow",
    "Kanpur",
    "Agra",
    "Varanasi",
    "Prayagraj",
    "Meerut",
    "Noida",
    "Gurugram",
    "Faridabad",
    "Amritsar",
    "Ludhiana",
    "Patiala",
    "Dehradun",
    "Haridwar",
    "Shimla",
    "Jammu",
    "Srinagar",
    "Patna",
    "Ranchi",
    "Bhubaneswar",
    "Guwahati",
    "Shillong",
    "Imphal",
)


def cases() -> list[dict[str, str]]:
    assert len(CITIES) == len(set(CITIES)) == 100
    return [
        {"id": f"india-{i:03}", "area": city, "query": f"{city}, India"}
        for i, city in enumerate(CITIES, 1)
    ]


def controls_for(origin: dict, departure: datetime) -> ConstraintSet:
    return ConstraintSet.model_validate(
        dict(
            origin=origin,
            departure_at=departure,
            duration_max_minutes=90,
            budget_minor_units=50000,
            currency_code="INR",
            budget_scope="PER_PERSON",
            party_mode="SOLO",
            party_size=1,
            vibes=["Explore"],
            hard_constraints=[],
            soft_constraints=[],
            max_walking_minutes=45,
            max_walking_meters=None,
            return_by_local=None,
            locale="en-IN",
            strict_budget=True,
        )
    )


def classify(status: int, body: dict, controls: ConstraintSet) -> str:
    if status == 200:
        result = CompiledPlan.model_validate(body)
        assert result.mode == "LIVE"
        assert all(e.source != "FIXTURE" for e in result.proof.sources)
        validation = validate_plan(result.plan, controls, as_of=result.compiled_at)
        assert validation.accepted and result.proof.validation.accepted
        assert all(c.status == "PASS" for c in result.proof.validation.checks)
        return "ACCEPTED_VERIFIED_PLAN"
    failure = CompilationFailure.model_validate(body)
    if status == 409:
        return "TYPED_REJECTION"
    if status == 429:
        return "RATE_LIMITED"
    if status == 503 and failure.code == "SOURCE_TEMPORARILY_UNAVAILABLE":
        return "TEMPORARY_PROVIDER_ERROR"
    return "API_OR_CONTRACT_FAILURE"


async def run(output: Path, departure: datetime, pause_seconds: float) -> None:
    inputs = cases()
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    report = (
        json.loads(output.read_text(encoding="utf-8"))
        if output.exists()
        else {
            "campaign": "100 distinct India starting areas, actual deployed API",
            "case_fingerprint": fingerprint,
            "departure_at": departure.isoformat(),
            "scope": "Scheduled daytime software compilation; no physical trips, no mocked sources",
            "started_at": datetime.now(UTC).isoformat(),
            "results": [],
        }
    )
    assert report["case_fingerprint"] == fingerprint
    assert report["departure_at"] == departure.isoformat()
    output.parent.mkdir(parents=True, exist_ok=True)
    completed = {r["id"] for r in report["results"]}
    async with httpx.AsyncClient(timeout=200, trust_env=False) as client:
        for case in inputs:
            if case["id"] in completed:
                continue
            started = perf_counter()
            receipt: dict = {**case, "executed_at": datetime.now(UTC).isoformat()}
            try:
                version = await client.get(API + "/v1/version")
                version.raise_for_status()
                receipt["version"] = version.json()
                search = await client.post(
                    API + "/v1/locations/search", json={"query": case["query"]}
                )
                receipt["search_http_status"] = search.status_code
                receipt["search_request_id"] = search.headers.get("X-Request-ID")
                locations = search.json()
                receipt["search_result"] = locations
                choices = [
                    p for p in locations.get("results", []) if "india" in p["label"].casefold()
                ]
                if search.status_code != 200 or not choices:
                    receipt["outcome"] = "LOCATION_SEARCH_FAILURE"
                else:
                    # Use the provider-selected public area; never invent a favourable origin.
                    controls = controls_for(choices[0]["coordinates"], departure)
                    receipt["controls"] = controls.model_dump(mode="json")
                    response = await client.post(
                        API + "/v1/plans/compile",
                        json={
                            "controls": receipt["controls"],
                            "free_text": "",
                            "mode": "LIVE",
                        },
                    )
                    receipt["compile_http_status"] = response.status_code
                    receipt["request_id"] = response.headers.get("X-Request-ID")
                    receipt["response"] = response.json()
                    receipt["outcome"] = classify(response.status_code, response.json(), controls)
                    retry = response.headers.get("Retry-After", "0")
                    receipt["retry_after_seconds"] = int(retry) if retry.isdigit() else 60
                after = await client.get(API + "/v1/version")
                after.raise_for_status()
                receipt["version_after"] = after.json()
                receipt["deployment_changed_during_case"] = (
                    receipt["version"]["commit"] != receipt["version_after"]["commit"]
                )
            except (httpx.HTTPError, ValueError, KeyError, TypeError, AssertionError) as error:
                receipt["outcome"] = "EXECUTION_OR_ORACLE_FAILURE"
                receipt["failure_kind"] = type(error).__name__
            receipt["latency_ms"] = round((perf_counter() - started) * 1000, 2)
            report["results"].append(receipt)
            report["completed_cases"] = len(report["results"])
            report["outcomes"] = dict(Counter(r["outcome"] for r in report["results"]))
            report["updated_at"] = datetime.now(UTC).isoformat()
            report["complete"] = len(report["results"]) == 100
            output.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            print(
                json.dumps(
                    {
                        "completed": report["completed_cases"],
                        "area": case["area"],
                        "outcome": receipt["outcome"],
                        "outcomes": report["outcomes"],
                    }
                ),
                flush=True,
            )
            if not report["complete"]:
                # Pace below six compiles/minute and obey the source cooldown.
                await asyncio.sleep(max(pause_seconds, receipt.get("retry_after_seconds", 0)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--departure", type=datetime.fromisoformat, required=True)
    parser.add_argument("--pause-seconds", type=float, default=12)
    args = parser.parse_args()
    if args.departure.tzinfo is None or args.pause_seconds < 12:
        parser.error("Timezone-aware departure and at least 12 seconds between journeys required")
    local = args.departure.astimezone(ZoneInfo("Asia/Kolkata"))
    print(
        f"Scheduled departure {local.isoformat()}; this is not an outing conducted now", flush=True
    )
    asyncio.run(run(args.output, args.departure, args.pause_seconds))
