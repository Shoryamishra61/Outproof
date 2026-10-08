"""Local Gemma selection over revalidated plans; model text cannot introduce venue facts."""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal, Protocol

import httpx
from ground_rule.models import CompilationFailure, ConstraintSet, Contract
from ground_rule.policy import validate_plan
from pydantic import ValidationError

from app.compiler import ValidCandidatePlan
from app.model_connection import model_connection


class RankSelection(Contract):
    selected_plan_id: str
    # Finite wording prevents hallucinated venues/operational assertions in a free-form reason.
    reason: Literal["Selected for your soft preferences."]


class ModelProvider(Protocol):
    async def generate(self, request: dict[str, object]) -> str | CompilationFailure: ...


class LocalGemma:
    def __init__(
        self,
        client: httpx.AsyncClient,
        model: str,
        base_url: str = "http://127.0.0.1:11434",
        api_key: str | None = None,
    ) -> None:
        self.base_url, self.headers = model_connection(base_url, api_key)
        self.client, self.model = client, model

    async def generate(self, request: dict[str, object]) -> str | CompilationFailure:
        try:
            response = await self.client.post(
                self.base_url + "/api/chat",
                json={**request, "model": self.model},
                timeout=120,
                headers=self.headers,
                follow_redirects=False,
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("done") is not True or not isinstance(
                payload["message"]["content"], str
            ):
                raise ValueError("Incomplete model response")
            return payload["message"]["content"]
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return CompilationFailure(
                code="MODEL_OUTPUT_INVALID", message="Local ranker unavailable or malformed"
            )


def ranker_request(
    plans: tuple[ValidCandidatePlan, ...], controls: ConstraintSet
) -> dict[str, object]:
    schema = RankSelection.model_json_schema()
    schema["properties"]["selected_plan_id"]["enum"] = [p.plan.plan_id for p in plans]
    prompt = (Path(__file__).resolve().parents[3] / "prompts/ranker.md").read_text(encoding="utf-8")
    summaries = [
        {
            "plan_id": item.plan.plan_id,
            "total_duration_seconds": item.plan.total_duration_seconds,
            "walking_distance_meters": item.plan.walking_distance_meters,
            "stop_count": len(item.plan.stops),
            "soft_fit_evidence": [
                e.value for s in item.plan.stops for e in s.place.evidence if e.field == "soft_fit"
            ],
        }
        for item in plans
    ]
    return {
        "stream": False,
        "think": False,
        "format": schema,
        "messages": [
            {
                "role": "user",
                "content": prompt
                + "\n"
                + json.dumps(
                    {
                        "soft_preferences": [s.preference for s in controls.soft_constraints],
                        "vibes": controls.vibes,
                        "valid_plans": summaries,
                        "output_schema": schema,
                    }
                ),
            }
        ],
        "options": {"temperature": 0, "seed": 42, "num_predict": 192, "num_ctx": 4096},
    }


def parse_selection(content: str, valid_ids: set[str]) -> RankSelection | CompilationFailure:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError("Duplicate output key")
        return result

    try:
        json.loads(content, object_pairs_hook=unique)
        selection = RankSelection.model_validate_json(content)
        if selection.selected_plan_id not in valid_ids:
            raise ValueError("Unknown/rejected selected plan")
        return selection
    except (ValueError, ValidationError):
        return CompilationFailure(
            code="MODEL_OUTPUT_INVALID", message="Ranker selection invalid; no facts altered"
        )


async def rank_valid_plans(
    plans: tuple[ValidCandidatePlan, ...],
    controls: ConstraintSet,
    model: ModelProvider,
    *,
    as_of: datetime,
    allow_fixture: bool = False,
) -> RankSelection | CompilationFailure:
    if not plans:
        return CompilationFailure(code="NO_GROUNDED_CANDIDATES", message="No valid plan to rank")
    ids = {p.plan.plan_id for p in plans}
    if len(ids) != len(plans) or any(
        not validate_plan(p.plan, controls, as_of=as_of, allow_fixture=allow_fixture).accepted
        or p.validation.plan_id != p.plan.plan_id
        or not p.validation.accepted
        for p in plans
    ):
        return CompilationFailure(
            code="MODEL_OUTPUT_INVALID", message="Ranker input is not a valid-plan set"
        )
    content = await model.generate(ranker_request(plans, controls))
    if isinstance(content, CompilationFailure):
        return content
    return parse_selection(content, ids)
