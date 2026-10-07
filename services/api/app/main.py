import asyncio
import os
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, Literal

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ground_rule.models import CompilationFailure, CompiledPlan, ConstraintSet, Contract
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError

from app.compilation import compile_internal
from app.fixtures import FixtureProviders
from app.parser import parse_constraints
from app.ranker import LocalGemma, ModelProvider


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    stage: Literal["bootstrap"]
    compilation_available: Literal[False]


class CompileRequest(Contract):
    controls: ConstraintSet
    free_text: Annotated[StrictStr, Field(max_length=4000)] = ""
    mode: Literal["FIXTURE"]


def create_app(
    *,
    fixture_enabled: bool = False,
    providers: FixtureProviders | None = None,
    model: ModelProvider | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> FastAPI:
    app = FastAPI(title="Ground Rule", version="0.1.0")

    @app.get("/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        # Fixture availability is separate from the unproven live acceptance gate.
        return HealthResponse(status="ok", stage="bootstrap", compilation_available=False)

    @app.post("/v1/plans/compile", response_model=CompiledPlan | CompilationFailure)
    async def compile_plan(request: Request) -> JSONResponse:
        if not fixture_enabled:
            return JSONResponse(
                status_code=503,
                content=CompilationFailure(
                    code="SOURCE_TEMPORARILY_UNAVAILABLE",
                    message="Public compilation disabled: real evidence gate has not passed",
                ).model_dump(mode="json"),
            )
        try:
            payload = await request.body()
            if len(payload) > 20000:
                raise ValueError("Oversized request")
            intake = CompileRequest.model_validate_json(payload)
        except (ValidationError, ValueError):
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
                    )
                if isinstance(controls, CompilationFailure):
                    result = controls
                else:
                    now = clock()
                    fixture = providers or FixtureProviders(as_of=now)
                    async with httpx.AsyncClient(trust_env=False) as client:
                        ranker = model or LocalGemma(
                            client,
                            os.environ.get("GEMMA_MODEL", "gemma4:e2b-it-qat"),
                            os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
                        )
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
        return JSONResponse(status_code=status, content=result.model_dump(mode="json"))

    return app


def fixture_configuration_enabled() -> bool:
    return (
        os.environ.get("GROUND_RULE_COMPILATION_ENABLED", "false").casefold() == "true"
        and os.environ.get("GROUND_RULE_FIXTURE_MODE", "false").casefold() == "true"
        and os.environ.get("GROUND_RULE_ENV") == "development"
    )


app = create_app(fixture_enabled=fixture_configuration_enabled())
