import asyncio

import httpx
import pytest
from app.main import create_app, fixture_configuration_enabled, live_configuration_enabled
from app.model_connection import model_connection
from app.ranker import LocalGemma
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
