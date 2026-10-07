"""Internal exactly-one compilation; public availability is a separate live-evidence gate."""

import logging
from collections.abc import Callable
from datetime import datetime
from time import perf_counter
from typing import Literal

from ground_rule.models import CompilationFailure, CompiledPlan, ConstraintSet
from ground_rule.proof import build_proof

from app.compiler import valid_candidate_plans
from app.enrichment import EnrichmentProvider
from app.places import PlacesProvider
from app.ranker import ModelProvider, rank_valid_plans
from app.routing import RoutingProvider


async def compile_internal(
    controls: ConstraintSet,
    discovery: PlacesProvider,
    enrichment: EnrichmentProvider,
    routing: RoutingProvider,
    model: ModelProvider,
    *,
    as_of: datetime,
    mode: Literal["FIXTURE", "LIVE", "CACHED"],
    clock: Callable[[], datetime] | None = None,
) -> CompiledPlan | CompilationFailure:
    started = perf_counter()
    valid = await valid_candidate_plans(
        controls, discovery, enrichment, routing, as_of=as_of, allow_fixture=mode == "FIXTURE"
    )
    if isinstance(valid, CompilationFailure):
        return valid
    if not valid:
        return CompilationFailure(
            code="NO_GROUNDED_CANDIDATES", message="No plan satisfied all hard checks"
        )
    selection = await rank_valid_plans(
        valid, controls, model, as_of=as_of, allow_fixture=mode == "FIXTURE"
    )
    if isinstance(selection, CompilationFailure):
        return selection
    selected = next(item for item in valid if item.plan.plan_id == selection.selected_plan_id)
    compiled_at = clock() if clock else as_of
    try:
        proof = build_proof(
            selected.plan,
            selected.validation,
            controls,
            as_of=compiled_at,
            allow_fixture=mode == "FIXTURE",
        )
        result = CompiledPlan(
            plan=selected.plan,
            proof=proof,
            reason=selection.reason,
            compiled_at=compiled_at,
            mode=mode,
        )
    except ValueError:
        return CompilationFailure(
            code="SOURCE_TEMPORARILY_UNAVAILABLE",
            message="Selected plan evidence expired or proof invalid; no success asserted",
        )
    logging.getLogger(__name__).info(
        "compiled mode=%s elapsed_ms=%.2f", mode, (perf_counter() - started) * 1000
    )
    return result
