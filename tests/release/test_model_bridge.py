import asyncio
import json

import httpx
import pytest
from app import model_bridge


def test_bridge_auth_bounds_busy_timeout_and_recovery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMMA_API_KEY", "synthetic-key")
    monkeypatch.setenv("OLLAMA_LOCAL_PORT", "11436")
    actual_client = httpx.AsyncClient
    calls: list[httpx.Request] = []
    should_timeout = False

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.url.host == "127.0.0.1" and request.url.port == 11436
        assert "authorization" not in request.headers
        if should_timeout:
            raise httpx.ReadTimeout("synthetic timeout", request=request)
        if request.method == "GET":
            return httpx.Response(
                200, json={"models": [{"name": "gemma4:e2b-it-qat"}, {"name": "other"}]}
            )
        payload = json.loads(request.content)
        assert payload["keep_alive"] == "30m"
        assert payload["options"]["num_predict"] == 512
        assert payload["options"]["num_ctx"] == 4096
        assert payload["think"] is False
        return httpx.Response(200, json={"done": True, "message": {"content": "{}"}})

    monkeypatch.setattr(
        model_bridge.httpx,
        "AsyncClient",
        lambda **kwargs: actual_client(transport=httpx.MockTransport(handle), **kwargs),
    )

    async def run() -> None:
        nonlocal should_timeout
        model_bridge.busy = asyncio.Lock()
        async with actual_client(
            transport=httpx.ASGITransport(app=model_bridge.app), base_url="http://bridge"
        ) as client:
            for headers in ({}, {"Authorization": "Bearer wrong"}):
                assert (await client.get("/api/tags", headers=headers)).status_code == 401
            assert not calls
            client.headers["Authorization"] = "Bearer synthetic-key"
            assert (await client.post("/api/pull", json={})).status_code == 404
            assert (await client.get("/docs")).status_code == 404
            await model_bridge.busy.acquire()
            assert (await client.post("/api/chat", json={})).status_code == 429
            tags = await client.get("/api/tags")
            assert tags.status_code == 200 and tags.json()["models"] == [
                {"name": "gemma4:e2b-it-qat"}
            ]
            model_bridge.busy.release()
            before = len(calls)
            payload = {
                "model": "gemma4:e2b-it-qat",
                "stream": False,
                "messages": [{"role": "user", "content": "synthetic input"}],
                "options": {"num_predict": 10000},
            }
            for invalid in (
                {**payload, "model": "other"},
                {**payload, "stream": True},
                {**payload, "messages": [{"role": "system", "content": "x"}]},
                {**payload, "options": None},
            ):
                assert (await client.post("/api/chat", json=invalid)).status_code == 503
            assert (await client.post("/api/chat", content=b"x" * 20001)).status_code == 503
            assert len(calls) == before
            should_timeout = True
            response = await client.post("/api/chat", json=payload)
            assert response.status_code == 503 and "synthetic" not in response.text
            assert not model_bridge.busy.locked()
            should_timeout = False
            assert (await client.post("/api/chat", json=payload)).status_code == 200

    asyncio.run(run())


@pytest.mark.parametrize("failure", [None, "timeout", "redirect", "oversize", "encoding"])
def test_source_relay_auth_allowlist_bounds_and_recovery(monkeypatch, failure):
    from app.reviewed_gardens import GARDENS

    monkeypatch.setenv("GEMMA_API_KEY", "synthetic-key")
    actual_client = httpx.AsyncClient
    calls = []

    def handle(request):
        calls.append(request)
        assert str(request.url) == GARDENS[0].url
        assert "authorization" not in request.headers
        if failure == "timeout":
            raise httpx.ConnectTimeout("synthetic", request=request)
        if failure == "redirect":
            return httpx.Response(301, headers={"Location": "http://169.254.169.254/"})
        if failure == "oversize":
            return httpx.Response(200, content=b"x" * 1_000_001)
        if failure == "encoding":
            return httpx.Response(200, content=b"\xff")
        return httpx.Response(200, text="<h1>Real upstream body</h1>")

    monkeypatch.setattr(
        model_bridge.httpx,
        "AsyncClient",
        lambda **kwargs: actual_client(transport=httpx.MockTransport(handle), **kwargs),
    )

    async def run():
        model_bridge.source_busy = asyncio.Lock()
        async with actual_client(
            transport=httpx.ASGITransport(app=model_bridge.app), base_url="http://bridge"
        ) as client:
            path = f"/sources/chandigarh/{GARDENS[0].park_way}"
            for headers in ({}, {"Authorization": "Bearer wrong"}):
                assert (await client.get(path, headers=headers)).status_code == 401
            assert not calls
            client.headers["Authorization"] = "Bearer synthetic-key"
            for invalid in ("999", "localhost", "http%3A%2F%2F169.254.169.254"):
                assert (await client.get("/sources/chandigarh/" + invalid)).status_code == 404
            assert not calls
            await model_bridge.source_busy.acquire()
            assert (await client.get(path)).status_code == 429
            model_bridge.source_busy.release()
            response = await client.get(path)
            assert response.status_code == (200 if failure is None else 503)
            assert len(calls) == 1 and not model_bridge.source_busy.locked()
            if failure is None:
                assert response.json()["source_url"] == GARDENS[0].url
                assert response.json()["html"] == "<h1>Real upstream body</h1>"
            else:
                assert "synthetic" not in response.text and "169.254" not in response.text

    asyncio.run(run())
