"""Bounded real public compilation gate; controlled tests are separate evidence."""

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
from app.reviewed_gardens import GARDENS
from ground_rule.models import CompilationFailure, CompiledPlan, ConstraintSet
from ground_rule.policy import validate_plan

from evals.runner.india_public import controls_for


async def verify(expected_commit: str, output: Path) -> None:
    api = "https://outproof-api.onrender.com"
    web = "https://outproof-web.onrender.com"
    report: dict = {
        "executed_at": datetime.now(UTC).isoformat(),
        "scope": "Real public API/model/source/routing; no mocks or physical outings",
        "expected_commit": expected_commit,
        "status": "FAIL",
        "results": [],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        async with httpx.AsyncClient(timeout=160, trust_env=False) as client:
            for attempt in range(10):
                version = await client.get(api + "/v1/version")
                version.raise_for_status()
                if version.json()["commit"] == expected_commit:
                    break
                if attempt == 9:
                    raise AssertionError("Public runtime does not match the requested commit")
                await asyncio.sleep(30)
            report["version"] = version.json()
            frontend = await client.get(web + "/")
            frontend.raise_for_status()
            assert "Outproof" in frontend.text
            report["frontend_http_status"] = frontend.status_code
            capabilities = await client.get(api + "/v1/capabilities")
            capabilities.raise_for_status()
            report["capabilities"] = capabilities.json()
            assert not capabilities.json()["fixture_enabled"]
            assert capabilities.json()["model"] == "gemma4:e2b-it-qat"
            cors = []
            for origin in (web, "https://untrusted.example"):
                response = await client.options(
                    api + "/v1/plans/compile",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "content-type",
                    },
                )
                allowed = response.headers.get("Access-Control-Allow-Origin")
                assert allowed == (web if origin == web else None)
                cors.append(
                    {"origin": origin, "http_status": response.status_code, "allowed": allowed}
                )
            report["cors"] = cors
            readiness = await client.get(api + "/v1/health/ready")
            report["readiness"] = {"http_status": readiness.status_code, "body": readiness.json()}
            assert readiness.status_code == 200 and readiness.json()["compilation_available"]
            search = await client.post(api + "/v1/locations/search", json={"query": "Chandigarh"})
            assert search.status_code == 200 and search.json()["results"]
            report["search"] = search.json()
            for kind in ("reviewed-walk", "zero-walking", "wrong-currency"):
                controls = controls_for(GARDENS[0].probe_origin.model_dump(), datetime.now(UTC))
                if kind == "zero-walking":
                    controls = ConstraintSet.model_validate(
                        controls.model_copy(update={"max_walking_minutes": 0})
                    )
                if kind == "wrong-currency":
                    controls = ConstraintSet.model_validate(
                        controls.model_copy(update={"currency_code": "USD"})
                    )
                response = await client.post(
                    api + "/v1/plans/compile",
                    json={
                        "mode": "LIVE",
                        "controls": controls.model_dump(mode="json"),
                        "free_text": "I prefer somewhere quiet. I'm not vegan."
                        if kind == "reviewed-walk"
                        else "",
                    },
                )
                row = {
                    "kind": kind,
                    "request_id": response.headers.get("X-Request-ID"),
                    "http_status": response.status_code,
                    "controls": controls.model_dump(mode="json"),
                    "body": response.json(),
                }
                report["results"].append(row)
                if kind == "reviewed-walk":
                    assert response.status_code == 200, (
                        "Reviewed public walk unavailable; not a passing release"
                    )
                    result = CompiledPlan.model_validate(response.json())
                    assert result.mode == "LIVE" and len(result.plan.stops) == 1
                    assert all(source.source != "FIXTURE" for source in result.proof.sources)
                    assert validate_plan(result.plan, controls, as_of=result.compiled_at).accepted
                else:
                    assert response.status_code == 409
                    CompilationFailure.model_validate(response.json())
                output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
                if kind != "wrong-currency":
                    await asyncio.sleep(12)
            after = await client.get(api + "/v1/version")
            assert after.json() == report["version"], "Runtime changed during verification"
            report["status"] = "PASS"
    except Exception as error:
        report["failure_kind"] = type(error).__name__
        raise
    finally:
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"status": report["status"], "results": len(report["results"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--output", type=Path, default=Path("artifacts/release/production-verification.json")
    )
    args = parser.parse_args()
    if len(args.commit) != 40 or any(c not in "0123456789abcdef" for c in args.commit):
        parser.error("An exact public commit SHA is required")
    asyncio.run(verify(args.commit, args.output))
