import asyncio

import httpx
from app.main import app


def test_health_reports_bootstrap_without_claiming_compilation() -> None:
    async def request() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.get("/v1/health")

    response = asyncio.run(request())
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "stage": "bootstrap",
        "compilation_available": False,
    }


def test_compile_endpoint_stays_unavailable_without_verified_compiler() -> None:
    async def request() -> httpx.Response:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            return await client.post("/v1/plans/compile", json={})

    response = asyncio.run(request())
    assert response.status_code == 503
    assert response.json()["code"] == "SOURCE_TEMPORARILY_UNAVAILABLE"
