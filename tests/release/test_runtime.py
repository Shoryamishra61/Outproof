import asyncio
from types import SimpleNamespace

import httpx
import pytest
from app.live import LivePlacesProvider
from app.main import create_app, fixture_configuration_enabled, live_configuration_enabled
from app.model_connection import model_connection
from app.ranker import LocalGemma
from app.reviewed_gardens import GARDENS
from app.routing import ValhallaRoutingProvider
from ground_rule.models import CompilationFailure


@pytest.mark.parametrize(
    "url",
    [
        "http://remote.example",
        "https://u:p@remote.example",
        "https://remote.example/?secret=x",
        "https://remote.example/#token",
        "file:///etc/passwd",
    ],
)
def test_remote_endpoint_boundary(url: str) -> None:
    with pytest.raises(ValueError):
        model_connection(url, "synthetic-key")


def test_authenticated_remote_model_does_not_follow_redirects() -> None:
    calls = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.headers["Authorization"] == "Bearer synthetic-key"
        return httpx.Response(302, headers={"Location": "http://127.0.0.1/private"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
            model = LocalGemma(
                client, "gemma4:e2b-it-qat", "https://model.example", "synthetic-key"
            )
            assert isinstance(await model.generate({}), CompilationFailure)
        assert len(calls) == 1

    asyncio.run(run())


@pytest.mark.parametrize("available_garden", [0, 1])
def test_singapore_outage_does_not_disable_a_verified_india_source(monkeypatch, available_garden):
    async def discover(self, origin, radius_meters):
        from app.live import GATE

        if origin == GATE:
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Controlled Singapore outage"
            )
        if origin != GARDENS[available_garden].coordinates:
            return CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Controlled first garden outage"
            )
        return (SimpleNamespace(coordinates=GARDENS[available_garden].coordinates),)

    async def route(*args, **kwargs):
        return SimpleNamespace(reachable=True)

    monkeypatch.setattr(LivePlacesProvider, "discover", discover)
    monkeypatch.setattr(ValhallaRoutingProvider, "route", route)

    async def run():
        async with httpx.AsyncClient() as model_client:
            app = create_app(live_enabled=True, model=LocalGemma(model_client, "gemma4:e2b-it-qat"))
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/v1/health/ready")
                assert response.status_code == 200
                assert (
                    response.json()["readiness_scope"]
                    == f"reviewed {GARDENS[available_garden].name} source and route only"
                )
                assert response.json()["global_compilation_verified"] is False
                regions = (await client.get("/v1/capabilities")).json()["verified_live_regions"]
                assert any("Shanti Kunj" in region for region in regions)

    asyncio.run(run())


@pytest.mark.parametrize("source_available", [True, False])
def test_concurrent_readiness_waits_for_one_real_probe(
    monkeypatch: pytest.MonkeyPatch, source_available: bool
) -> None:
    async def run() -> None:
        entered = asyncio.Event()
        release = asyncio.Event()
        calls = 0

        async def discover(*args: object, **kwargs: object) -> list | CompilationFailure:
            nonlocal calls
            calls += 1
            entered.set()
            await release.wait()
            return (
                (SimpleNamespace(coordinates=args[1]),)
                if source_available
                else CompilationFailure(
                    code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Controlled source outage"
                )
            )

        async def route(*args: object, **kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(reachable=True)

        monkeypatch.setattr(LivePlacesProvider, "discover", discover)
        monkeypatch.setattr(ValhallaRoutingProvider, "route", route)
        async with httpx.AsyncClient() as model_client:
            app = create_app(live_enabled=True, model=LocalGemma(model_client, "gemma4:e2b-it-qat"))
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://test"
            ) as client:
                first = asyncio.create_task(client.get("/v1/health/ready"))
                await asyncio.wait_for(entered.wait(), timeout=1)
                second = asyncio.create_task(client.get("/v1/health/ready"))
                try:
                    await asyncio.wait_for(asyncio.shield(second), timeout=0.05)
                    pytest.fail("Readiness answered before the in-flight provider probe completed")
                except TimeoutError:
                    pass
                finally:
                    release.set()
                    responses = await asyncio.gather(first, second)
                assert calls == (1 if source_available else 3)
                assert responses[0].json() == responses[1].json()
                assert all(r.status_code == (200 if source_available else 503) for r in responses)
                assert responses[0].json()["compilation_available"] is source_available
                assert responses[0].json()["global_compilation_verified"] is False
                assert responses[0].json()["readiness_scope"] == (
                    "reviewed Singapore source and route only"
                    if source_available
                    else "reviewed Singapore and Chandigarh probes; selected area not checked"
                )
                assert (await client.get("/v1/health/ready")).json() == responses[0].json()
                assert calls == (1 if source_available else 3)

    asyncio.run(run())


def test_production_cannot_enable_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [
        "GROUND_RULE_COMPILATION_ENABLED",
        "GROUND_RULE_LIVE_MODE",
        "GROUND_RULE_FIXTURE_MODE",
    ]:
        monkeypatch.setenv(key, "true")
    monkeypatch.setenv("GROUND_RULE_ENV", "production")
    assert not fixture_configuration_enabled() and not live_configuration_enabled()


def test_liveness_is_distinct_from_ready_and_requests_are_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://unconfigured.example")
    monkeypatch.delenv("GEMMA_API_KEY", raising=False)

    async def run() -> None:
        app = create_app(live_enabled=True)
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            assert (await client.get("/v1/health/live")).status_code == 200
            capabilities = (await client.get("/v1/capabilities")).json()
            assert capabilities["live_evidence_configured"]
            assert "live_evidence_available" not in capabilities
            ready = await client.get("/v1/health/ready")
            assert ready.status_code == 503 and not ready.json()["live_evidence_available"]
            for _ in range(6):
                response = await client.post("/v1/plans/compile", content=b"x" * 20001)
                assert response.status_code == 422
                assert len(response.headers["X-Request-ID"]) == 32
                assert response.headers["Cache-Control"] == "no-store"
            limited = await client.post("/v1/plans/compile", json={})
            assert limited.status_code == 429 and limited.headers["Retry-After"] == "60"

    asyncio.run(run())
