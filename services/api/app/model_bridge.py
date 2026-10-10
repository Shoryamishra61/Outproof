"""Authenticated, bounded model calls and reviewed official-page transport."""

import asyncio
import json
import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, nullcontext
from datetime import UTC, datetime

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.reviewed_gardens import GARDENS, read_reviewed_source


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if os.name == "nt":
        import ctypes

        ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        yield
    finally:
        if os.name == "nt":
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
busy = asyncio.Lock()
source_busy = asyncio.Lock()


@app.get("/sources/chandigarh/{park_way}")
@app.get("/sources/gardens/{park_way}")
async def official_garden(park_way: str, request: Request) -> JSONResponse:
    key = os.getenv("GEMMA_API_KEY", "")
    if not key or not secrets.compare_digest(
        request.headers.get("Authorization", ""), "Bearer " + key
    ):
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    garden = next((g for g in GARDENS if str(g.park_way) == park_way), None)
    if garden is None:
        return JSONResponse(status_code=404, content={"error": "Unsupported source"})
    if source_busy.locked():
        return JSONResponse(status_code=429, content={"error": "Source busy"})
    try:
        async with source_busy, httpx.AsyncClient(trust_env=False) as client:
            html = (await read_reviewed_source(client, garden.url)).decode("utf-8")
            return JSONResponse(
                headers={"Cache-Control": "no-store"},
                content={
                    "source_url": garden.url,
                    "observed_at": datetime.now(UTC).isoformat(),
                    "html": html,
                },
            )
    except (httpx.HTTPError, ValueError):
        return JSONResponse(status_code=503, content={"error": "Reviewed source unavailable"})


@app.api_route("/api/{operation}", methods=["GET", "POST"])
async def proxy(operation: str, request: Request) -> JSONResponse:
    key = os.getenv("GEMMA_API_KEY", "")
    if not key or not secrets.compare_digest(
        request.headers.get("Authorization", ""), "Bearer " + key
    ):
        return JSONResponse(status_code=401, content={"error": "Authentication required"})
    if (operation, request.method) not in {("tags", "GET"), ("chat", "POST")}:
        return JSONResponse(status_code=404, content={"error": "Unsupported operation"})
    if operation == "chat" and busy.locked():
        return JSONResponse(status_code=429, content={"error": "Model busy"})
    model = os.getenv("GEMMA_MODEL", "gemma4:e2b-it-qat")
    try:
        payload: dict = {}
        if operation == "chat":
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 20000:
                    raise ValueError("Oversized request")
            payload = json.loads(body)
            if (
                not isinstance(payload, dict)
                or payload.get("model") != model
                or payload.get("stream") is not False
            ):
                raise ValueError("Unsupported request")
            messages = payload.get("messages")
            if (
                not isinstance(messages, list)
                or not 1 <= len(messages) <= 2
                or any(
                    not isinstance(m, dict)
                    or m.get("role") != "user"
                    or not isinstance(m.get("content"), str)
                    for m in messages
                )
            ):
                raise ValueError("Unsupported messages")
            payload = {
                "model": model,
                "messages": messages,
                "format": payload.get("format"),
                "stream": False,
                "think": False,
                "keep_alive": "30m",
                "options": {
                    "temperature": 0,
                    "seed": 42,
                    "num_ctx": 4096,
                    "num_predict": min(
                        512, max(1, int(payload.get("options", {}).get("num_predict", 384)))
                    ),
                },
            }
        async with (
            busy if operation == "chat" else nullcontext(),
            httpx.AsyncClient(trust_env=False, timeout=125) as client,
        ):
            port = int(os.getenv("OLLAMA_LOCAL_PORT", "11436"))
            if not 1 <= port <= 65535:
                raise ValueError("Invalid local model port")
            url = f"http://127.0.0.1:{port}/api/" + operation
            response = await (
                client.get(url) if operation == "tags" else client.post(url, json=payload)
            )
            response.raise_for_status()
            output = response.json()
            if operation == "tags":
                output = {"models": [m for m in output["models"] if m["name"] == model]}
            return JSONResponse(content=output)
    except (httpx.HTTPError, ValueError, KeyError, TypeError, AttributeError):
        return JSONResponse(
            status_code=503, content={"error": "Model unavailable or request invalid"}
        )
