"""Bounded ASGI staging load with controlled providers; zero public map requests."""

import asyncio
import json
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from time import perf_counter

import httpx
from app.fixtures import FixtureProviders
from app.main import create_app
from fastapi import FastAPI


class ControlledModel:
    async def generate(self, request: dict) -> str:
        await asyncio.sleep(0.05)
        return json.dumps(
            {
                "selected_plan_id": request["format"]["properties"]["selected_plan_id"]["enum"][0],
                "reason": "Selected for your soft preferences.",
            }
        )


async def main() -> None:
    tracemalloc.start()
    rows = []
    for users in [1, 5, 10, 25]:
        fixture = FixtureProviders()
        app = create_app(
            fixture_enabled=True,
            providers=fixture,
            model=ControlledModel(),
            clock=lambda observed=fixture.as_of: observed,
        )

        async def request(
            index: int, application: FastAPI = app, provider: FixtureProviders = fixture
        ) -> dict:
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=application, client=(f"controlled-{index}", 1)),
                base_url="http://staging",
            ) as client:
                start = perf_counter()
                response = await client.post(
                    "/v1/plans/compile",
                    json={
                        "mode": "FIXTURE",
                        "controls": provider.controls.model_dump(mode="json"),
                        "free_text": "",
                    },
                )
                body = response.json()
                assert response.status_code in {200, 429}, (response.status_code, body)
                assert (body["status"] == "SUCCESS") == (response.status_code == 200)
                if response.status_code == 200:
                    assert (
                        body["mode"] == "FIXTURE"
                        and len(body["proof"]["validation"]["checks"]) == 11
                    )
                else:
                    assert response.headers["Retry-After"] == "60"
                return {
                    "status": response.status_code,
                    "latency_ms": (perf_counter() - start) * 1000,
                    "request_id": response.headers["X-Request-ID"],
                }

        responses = await asyncio.gather(*(request(index) for index in range(users)))
        assert len({r["request_id"] for r in responses}) == users
        latencies = sorted(r["latency_ms"] for r in responses)
        successes = sum(r["status"] == 200 for r in responses)
        assert successes == min(users, 2)
        # Capacity admission must recover after every controlled burst.
        recovered = await request(users + 1)
        assert recovered["status"] == 200
        rows.append(
            {
                "users": users,
                "successes": successes,
                "bounded_429": users - successes,
                "unexpected_errors": 0,
                "p50_ms": median(latencies),
                "p95_ms": latencies[min(users - 1, int(users * 0.95))],
                "p99_ms": latencies[-1],
                "recovery": recovered,
                "responses": responses,
            }
        )
    report = {
        "executed_at": datetime.now(UTC).isoformat(),
        "scope": (
            "controlled ASGI staging; synthetic providers and model; "
            "no public load or physical outings"
        ),
        "bursts": rows,
        "python_peak_allocated_bytes": tracemalloc.get_traced_memory()[1],
    }
    Path("evals/reports/release-controlled-load.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(
        json.dumps(
            [
                {k: r[k] for k in ["users", "successes", "bounded_429", "unexpected_errors"]}
                for r in rows
            ]
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
