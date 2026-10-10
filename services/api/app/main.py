import asyncio
import hashlib
import logging
import os
import secrets
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from math import ceil
from time import monotonic, perf_counter
from typing import Annotated, Literal
from uuid import uuid4

import httpx
import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from ground_rule.models import (
    CompilationFailure,
    CompiledPlan,
    ConstraintSet,
    Contract,
    Coordinates,
)
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError

from app.compilation import compile_internal
from app.enrichment import EnrichmentProvider
from app.fixtures import FixtureProviders
from app.geocoding import LocationResults, LocationSearchProvider
from app.live import GATE, LiveEnrichmentProvider, LivePlacesProvider
from app.model_connection import model_connection
from app.observability import configure
from app.parser import parse_constraints
from app.places import OverpassAvailability, PlacesProvider
from app.ranker import LocalGemma, ModelProvider
from app.reviewed_gardens import GARDENS
from app.routing import RoutingProvider, ValhallaRoutingProvider
from app.source_discovery import SerpSourceDiscovery


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    stage: Literal["bootstrap"]
    compilation_available: Literal[False]


class CompileRequest(Contract):
    controls: ConstraintSet
    free_text: Annotated[StrictStr, Field(max_length=4000)] = ""
    mode: Literal["FIXTURE", "LIVE"]


class LocationSearchRequest(Contract):
    query: Annotated[StrictStr, Field(min_length=2, max_length=160)]


def create_app(
    *,
    fixture_enabled: bool = False,
    live_enabled: bool = False,
    providers: FixtureProviders | None = None,
    live_discovery: PlacesProvider | None = None,
    live_enrichment: EnrichmentProvider | None = None,
    live_routing: RoutingProvider | None = None,
    model: ModelProvider | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> FastAPI:
    configure()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    technical_logger = logging.getLogger("app")
    technical_logger.setLevel(logging.INFO)
    if not technical_logger.handlers:
        technical_logger.addHandler(logging.StreamHandler())
    app = FastAPI(title="Outproof", version="0.1.0")
    origins = [s.strip() for s in os.getenv("GROUND_RULE_CORS_ORIGINS", "").split(",") if s.strip()]
    if "*" in origins:
        raise ValueError("Explicit CORS origins required")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        expose_headers=["X-Request-ID", "Retry-After"],
    )
    hosts = os.getenv("GROUND_RULE_ALLOWED_HOSTS", "*").split(",")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)
    active_compiles = 0
    ready_cache: tuple[float, dict[str, object]] | None = None
    ready_lock = asyncio.Lock()
    recent: dict[str, deque[float]] = {}
    salt = secrets.token_bytes(32)
    overpass_availability = OverpassAvailability()
    geocoder = LocationSearchProvider(os.getenv("GEOCODER_URL", "https://photon.komoot.io/api/"))
    search = SerpSourceDiscovery(
        os.getenv("SERPAPI_API_KEY") if os.getenv("GROUND_RULE_SERPAPI_ENABLED") == "true" else None
    )

    @app.middleware("http")
    async def protect_request(request: Request, call_next: Callable) -> JSONResponse:
        nonlocal active_compiles
        request_id = uuid4().hex
        started = perf_counter()
        is_compile = request.method == "POST" and request.url.path == "/v1/plans/compile"
        response = None
        acquired = False
        if is_compile:
            now = monotonic()
            for key in list(recent):
                while recent[key] and recent[key][0] <= now - 60:
                    recent[key].popleft()
                if not recent[key]:
                    del recent[key]
            address = request.client.host if request.client else "unknown"
            key = hashlib.sha256(salt + address.encode()).hexdigest()
            if active_compiles >= 2 or len(recent.get(key, ())) >= 6 or len(recent) >= 2048:
                response = JSONResponse(
                    status_code=429,
                    headers={"Retry-After": "60"},
                    content=CompilationFailure(
                        code="SOURCE_TEMPORARILY_UNAVAILABLE",
                        message="Compilation capacity reached; retry later",
                    ).model_dump(mode="json"),
                )
            else:
                recent.setdefault(key, deque()).append(now)
                active_compiles += 1
                acquired = True
        try:
            if response is None:
                with sentry_sdk.start_transaction(
                    op="http.server",
                    name="ground_rule.compile" if is_compile else "ground_rule.system",
                ) as transaction:
                    response = await call_next(request)
                    transaction.set_http_status(response.status_code)
        finally:
            if acquired:
                active_compiles -= 1
        response.headers.update(
            {
                "X-Request-ID": request_id,
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Referrer-Policy": "no-referrer",
                "Cache-Control": "no-store",
            }
        )
        logging.getLogger(__name__).info(
            "request id=%s status=%s elapsed_ms=%.2f",
            request_id,
            response.status_code,
            (perf_counter() - started) * 1000,
        )
        return response

    @app.get("/v1/health/live")
    def liveness() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/locations/search", response_model=LocationResults | CompilationFailure)
    async def search_locations(request: Request) -> JSONResponse:
        try:
            payload = bytearray()
            async for chunk in request.stream():
                payload.extend(chunk)
                if len(payload) > 2048:
                    raise ValueError("Oversized search request")
            query = LocationSearchRequest.model_validate_json(payload).query.strip()
            if len(query) < 2:
                raise ValueError("Search text is too short")
        except (ValidationError, ValueError):
            return JSONResponse(
                status_code=422, content={"detail": "Enter a place or area (2–160 characters)"}
            )
        async with httpx.AsyncClient(trust_env=False) as client:
            status, result = await geocoder.search(query, client)
        return JSONResponse(
            status_code=status,
            content=result.model_dump(mode="json"),
            headers={"Retry-After": "1"} if status == 429 else None,
        )

    @app.get("/v1/version")
    def version() -> dict[str, str]:
        return {
            "version": "0.1.0",
            "commit": os.getenv("RENDER_GIT_COMMIT", "local"),
            "environment": os.getenv("GROUND_RULE_ENV", "development"),
        }

    @app.get("/v1/capabilities")
    def capabilities() -> dict[str, object]:
        return {
            "fixture_enabled": fixture_enabled,
            "live_enabled": live_enabled,
            "verified_live_regions": [
                "Singapore Botanic Gardens Tanglin entrance corridor",
                *(
                    f"{garden.name}, {garden.city} mapped pedestrian access corridor"
                    for garden in GARDENS
                ),
            ],
            "live_evidence_configured": live_enabled,
            "model": os.getenv("GEMMA_MODEL", "gemma4:e2b-it-qat"),
            "offline_compilation": False,
            "optional_integrations": {
                "serpapi_configured": bool(search.key),
                "sentry_configured": bool(os.getenv("SENTRY_DSN")),
            },
        }

    @app.get("/v1/health/ready")
    async def readiness() -> JSONResponse:
        nonlocal ready_cache
        async with ready_lock:
            if ready_cache and ready_cache[0] > monotonic():
                value = ready_cache[1]
                return JSONResponse(
                    status_code=200 if value["compilation_available"] else 503, content=value
                )
            response = await probe_readiness()
            import json

            ready_cache = (monotonic() + 60, json.loads(response.body))
            return response

    async def probe_readiness() -> JSONResponse:
        reachable = model is not None
        if not reachable:
            try:
                endpoint, headers = model_connection(
                    os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                    os.getenv("GEMMA_API_KEY"),
                )
                async with httpx.AsyncClient(trust_env=False, timeout=5) as client:
                    response = await client.get(endpoint + "/api/tags", headers=headers)
                    response.raise_for_status()
                    names = {m["name"] for m in response.json()["models"]}
                    reachable = os.getenv("GEMMA_MODEL", "gemma4:e2b-it-qat") in names
            except (httpx.HTTPError, ValueError, KeyError, TypeError):
                reachable = False
        source_ready = False
        source_scope = "reviewed Singapore and India probes; selected area not checked"
        if live_enabled and reachable:
            async with httpx.AsyncClient(trust_env=False) as client:
                discovery = LivePlacesProvider(
                    client, os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
                )
                routing = ValhallaRoutingProvider(
                    client, os.getenv("VALHALLA_BASE_URL", "https://valhalla1.openstreetmap.de")
                )
                try:
                    async with asyncio.timeout(45):
                        for name, access, start in (
                            ("Singapore", GATE, Coordinates(latitude=1.3068, longitude=103.819)),
                            *((g.name, g.coordinates, g.probe_origin) for g in GARDENS),
                        ):
                            places = await discovery.discover(access, 1000)
                            if isinstance(places, CompilationFailure) or not places:
                                continue
                            route = await routing.route(
                                "probe", "access", start, places[0].coordinates
                            )
                            if not isinstance(route, CompilationFailure) and route.reachable:
                                source_ready = True
                                source_scope = f"reviewed {name} source and route only"
                                break
                except TimeoutError:
                    source_ready = False
        ready = reachable and (fixture_enabled or (live_enabled and source_ready))
        return JSONResponse(
            status_code=200 if ready else 503,
            content={
                "status": "ready" if ready else "unavailable",
                "model_reachable": reachable,
                "live_evidence_available": source_ready,
                "compilation_available": ready,
                "mode": ("FIXTURE" if fixture_enabled else "LIVE") if ready else None,
                "readiness_scope": source_scope if live_enabled else "development fixtures only",
                "global_compilation_verified": False,
            },
        )

    @app.get("/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        # Fixture/live availability is separate from the unproven live acceptance gate.
        return HealthResponse(status="ok", stage="bootstrap", compilation_available=False)

    @app.post("/v1/plans/compile", response_model=CompiledPlan | CompilationFailure)
    async def compile_plan(request: Request) -> JSONResponse:
        if not (fixture_enabled or live_enabled):
            return JSONResponse(
                status_code=503,
                content=CompilationFailure(
                    code="SOURCE_TEMPORARILY_UNAVAILABLE",
                    message="Public compilation disabled: real evidence gate has not passed",
                ).model_dump(mode="json"),
            )
        try:
            payload = bytearray()
            async for chunk in request.stream():
                payload.extend(chunk)
                if len(payload) > 20000:
                    raise ValueError("Oversized request")
            intake = CompileRequest.model_validate_json(payload)
        except (ValidationError, ValueError):
            return JSONResponse(
                status_code=422,
                content=CompilationFailure(
                    code="MODEL_OUTPUT_INVALID",
                    message="Malformed compile request; explicit enabled mode required",
                ).model_dump(mode="json"),
            )
        if intake.mode == "LIVE" and not live_enabled:
            return JSONResponse(
                status_code=422,
                content=CompilationFailure(
                    code="MODEL_OUTPUT_INVALID",
                    message="Malformed compile request; explicit FIXTURE mode required",
                ).model_dump(mode="json"),
            )
        if intake.mode == "FIXTURE" and not fixture_enabled:
            return JSONResponse(
                status_code=422,
                content=CompilationFailure(
                    code="MODEL_OUTPUT_INVALID",
                    message="Malformed compile request; explicit FIXTURE mode required",
                ).model_dump(mode="json"),
            )
        controls = intake.controls
        try:
            async with asyncio.timeout(180):
                if intake.free_text.strip():
                    controls = await asyncio.to_thread(
                        parse_constraints,
                        controls,
                        intake.free_text,
                        model=os.environ.get("GEMMA_MODEL", "gemma4:e2b-it-qat"),
                        base_url=os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                        api_key=os.getenv("GEMMA_API_KEY"),
                    )
                if isinstance(controls, CompilationFailure):
                    result = controls
                else:
                    now = clock()
                    async with httpx.AsyncClient(trust_env=False) as client:
                        ranker = model or LocalGemma(
                            client,
                            os.environ.get("GEMMA_MODEL", "gemma4:e2b-it-qat"),
                            os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                            api_key=os.getenv("GEMMA_API_KEY"),
                        )
                        if intake.mode == "LIVE":
                            discovery = live_discovery or LivePlacesProvider(
                                client,
                                os.getenv(
                                    "OVERPASS_URL", "https://overpass-api.de/api/interpreter"
                                ),
                                search=search,
                                availability=overpass_availability,
                            )
                            enrichment = live_enrichment or LiveEnrichmentProvider(clock=clock)
                            routing = live_routing or ValhallaRoutingProvider(
                                client,
                                os.environ.get(
                                    "VALHALLA_BASE_URL", "https://valhalla1.openstreetmap.de"
                                ),
                            )
                            result = await compile_internal(
                                controls,
                                discovery,
                                enrichment,
                                routing,
                                ranker,
                                as_of=now,
                                mode="LIVE",
                                clock=clock,
                            )
                        else:
                            fixture = providers or FixtureProviders(as_of=now)
                            result = await compile_internal(
                                controls,
                                fixture,
                                fixture,
                                fixture,
                                ranker,
                                as_of=now,
                                mode="FIXTURE",
                                clock=clock,
                            )
        except (TimeoutError, httpx.HTTPError):
            result = CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE", message="Compilation/provider timeout"
            )
        except ValueError:
            result = CompilationFailure(
                code="MODEL_OUTPUT_INVALID", message="Contract or model configuration invalid"
            )
        except Exception:
            sentry_sdk.capture_message("INTERNAL_COMPILATION_FAILURE", level="error")
            logging.getLogger(__name__).error(
                "Internal compilation failure; private context omitted"
            )
            result = CompilationFailure(
                code="SOURCE_TEMPORARILY_UNAVAILABLE",
                message="Internal compilation failure; no plan asserted",
            )
        status = (
            200
            if isinstance(result, CompiledPlan)
            else (
                503
                if result.code == "SOURCE_TEMPORARILY_UNAVAILABLE"
                else 422
                if result.code == "MODEL_OUTPUT_INVALID"
                else 409
            )
        )
        retry_seconds = ceil(overpass_availability.retry_at - monotonic())
        return JSONResponse(
            status_code=status,
            content=result.model_dump(mode="json"),
            headers={"Retry-After": str(retry_seconds)}
            if status == 503 and retry_seconds > 0
            else None,
        )

    return app


def fixture_configuration_enabled() -> bool:
    return (
        os.environ.get("GROUND_RULE_COMPILATION_ENABLED", "false").casefold() == "true"
        and os.environ.get("GROUND_RULE_FIXTURE_MODE", "false").casefold() == "true"
        and os.environ.get("GROUND_RULE_ENV") == "development"
    )


def live_configuration_enabled() -> bool:
    return (
        os.environ.get("GROUND_RULE_COMPILATION_ENABLED", "false").casefold() == "true"
        and os.environ.get("GROUND_RULE_LIVE_MODE", "false").casefold() == "true"
        and os.environ.get("GROUND_RULE_ENV") in {"development", "production"}
        and os.environ.get("GROUND_RULE_FIXTURE_MODE", "false").casefold() != "true"
    )


app = create_app(
    fixture_enabled=fixture_configuration_enabled(),
    live_enabled=live_configuration_enabled(),
)
