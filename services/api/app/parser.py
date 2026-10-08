"""Local Gemma interprets additions; deterministic merging owns control precedence."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Literal

import httpx
from ground_rule.models import (
    CompilationFailure,
    ConstraintSet,
    Contract,
    HardConstraint,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    SoftConstraint,
)
from pydantic import AwareDatetime, Field, ValidationError

from app.model_connection import model_connection

Preference = Literal[
    "quiet",
    "cheap",
    "low walking",
    "optional coffee",
    "optional food",
    "talk",
    "romantic",
    "open late",
    "uncrowded",
    "explore",
    "short outing",
]
Unsupported = Literal[
    "allergy safety", "wheelchair accessibility", "personal safety", "time clarification"
]


class ParserAdditions(Contract):
    exclusions: tuple[Literal["mall", "alcohol", "chain"], ...] = Field(max_length=3)
    dietary: Literal["vegetarian", "vegan"] | None
    unsupported: tuple[Unsupported, ...] = Field(max_length=4)
    preferences: tuple[Preference, ...] = Field(max_length=11)
    party_size: PositiveInt | None
    max_walking_minutes: NonNegativeInt | None
    max_walking_meters: NonNegativeFloat | None
    return_by_local: AwareDatetime | None


def protected_requirements(text: str) -> tuple[Unsupported, ...]:
    """Retain explicit high-stakes requirements even when the model omits them."""
    requirements: list[Unsupported] = []
    if re.search(r"\ballerg\w*\b|\banaphyl\w*\b", text, re.I):
        requirements.append("allergy safety")
    if re.search(r"\bwheelchair\b|\baccessible\b|\baccessibility\b", text, re.I):
        requirements.append("wheelchair accessibility")
    if re.search(r"\bsafety guarantee\b|\bguaranteed safe\b|\b100% safe\b", text, re.I):
        requirements.append("personal safety")
    if re.search(
        r"\b(?:back|return)\b.*?\b(?:by|before)\s+\d{1,2}(?::\d{2})?(?:\s*(?:am|pm))?\b", text, re.I
    ):
        requirements.append("time clarification")
    return tuple(requirements)


def merge_additions(
    controls: ConstraintSet,
    text: str,
    additions: ParserAdditions,
) -> ConstraintSet | CompilationFailure:
    """Preserve supplied controls; fill only absent optional fields with sourced values."""
    controls = ConstraintSet.model_validate(controls)
    additions = ParserAdditions.model_validate(additions)
    for category, token in (("mall", r"malls?"), ("alcohol", r"alcohol"), ("chain", r"chains?")):
        requested = bool(
            re.search(
                rf"\b(?:no|avoid|exclude)\s+(?:crowded\s+)?"
                rf"(?:(?:malls?|alcohol|chains?)\s+(?:or|and)\s+)*{token}\b|"
                rf"\b{token}(?:\s+\w+){{0,3}}\s+(?:nahi|mat)\b",
                text,
                re.I,
            )
        )
        forbidden = bool(
            re.search(
                rf"\b{token}\s+(?:are\s+)?(?:fine|okay)\b|\bdon't exclude\s+{token}\b",
                text,
                re.I,
            )
        )
        requested = requested and not forbidden
        emitted = category in additions.exclusions
        if (requested and not emitted) or (
            emitted and (forbidden or not re.search(rf"\b{token}\b", text, re.I))
        ):
            return CompilationFailure(
                code="MODEL_OUTPUT_INVALID",
                message="Explicit exclusion conflicts with model extraction",
            )
    dietary_words = re.findall(r"\b(?:vegetarian|vegan|veg)\b", text, re.I)
    negated_diet = re.search(
        r"\b(?:do not|don't)\s+require\s+(?:vegetarian|vegan|veg)\b", text, re.I
    )
    required_diet = (
        "vegan" if any(word.casefold() == "vegan" for word in dietary_words) else "vegetarian"
    )
    if (dietary_words and not negated_diet and additions.dietary != required_diet) or (
        additions.dietary is not None and (not dietary_words or negated_diet)
    ):
        return CompilationFailure(
            code="MODEL_OUTPUT_INVALID",
            message="Explicit dietary requirement conflicts with model extraction",
        )
    protected = protected_requirements(text)
    if any(value not in protected for value in additions.unsupported):
        return CompilationFailure(
            code="MODEL_OUTPUT_INVALID",
            message="Unsupported requirement lacks explicit source text",
        )
    walking_clause = re.search(
        r"\b(?:max(?:imum)?\s+walk(?:ing)?|walk(?:ing)?\s+max(?:imum)?)\s+([^,;]+)",
        text,
        re.I,
    )
    if walking_clause:
        for number, unit in re.findall(
            r"(\d+(?:\.\d+)?)\s*(minutes?|mins?|meters?|metres?)\b", walking_clause[1], re.I
        ):
            field = (
                "max_walking_minutes" if unit.casefold().startswith("min") else "max_walking_meters"
            )
            expected = float(number)
            supplied = getattr(controls, field)
            proposal = getattr(additions, field)
            if (supplied is not None and supplied != expected) or (
                supplied is None and proposal != expected
            ):
                return CompilationFailure(
                    code="MODEL_OUTPUT_INVALID",
                    message="Explicit walking limit missing or conflicts with a control",
                )
    explicit_deadline = re.search(
        r"\b(?:back|return)\s+(?:by|before)\s+"
        r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2}))",
        text,
        re.I,
    )
    if explicit_deadline and controls.return_by_local is None and additions.return_by_local is None:
        return CompilationFailure(
            code="MODEL_OUTPUT_INVALID", message="Explicit dated deadline missing from extraction"
        )
    updates: dict[str, object] = {}
    for field in ("party_size", "max_walking_minutes", "max_walking_meters", "return_by_local"):
        proposal = getattr(additions, field)
        supplied = getattr(controls, field)
        if proposal is None:
            continue
        if supplied is not None:
            return CompilationFailure(
                code="MODEL_OUTPUT_INVALID",
                message=f"Model emitted authoritative {field}; its requested proposal must be null",
            )
        if isinstance(proposal, datetime):
            # An offset-aware date must be explicitly supplied; never invent today's date.
            dates = re.findall(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:\d{2})", text
            )
            if not any(datetime.fromisoformat(value) == proposal for value in dates):
                return CompilationFailure(
                    code="MODEL_OUTPUT_INVALID", message="Deadline lacks an explicit dated instant"
                )
        else:
            number = re.escape(str(proposal).removesuffix(".0"))
            if field == "party_size":
                pattern = rf"\b{number}\s+(?:of us|people|persons|friends)\b|\bparty of {number}\b"
            else:
                unit = (
                    r"(?:minutes?|mins?)"
                    if field == "max_walking_minutes"
                    else r"(?:meters?|metres?|m)"
                )
                pattern = (
                    rf"\b(?:max(?:imum)?\s+walk(?:ing)?|walk(?:ing)?\s+max(?:imum)?)"
                    rf"\s+[^,.;]{{0,48}}?(?<![\d.]){number}\s*{unit}\b"
                )
            if not re.search(pattern, text, re.I):
                return CompilationFailure(
                    code="MODEL_OUTPUT_INVALID",
                    message=f"Model lacks explicit numeric evidence for {field}",
                )
        updates[field] = proposal
    hard = list(controls.hard_constraints)
    hard.extend(
        HardConstraint(kind="EXCLUDE_CATEGORY", value=value) for value in additions.exclusions
    )
    if additions.dietary:
        hard.append(HardConstraint(kind="DIETARY", value=additions.dietary))
    for value in dict.fromkeys((*additions.unsupported, *protected)):
        if value == "time clarification" and controls.return_by_local is not None:
            continue
        hard.append(HardConstraint(kind="UNSUPPORTED", value=value))
    if any(
        value != "time clarification" or controls.return_by_local is None for value in protected
    ):
        hard.append(HardConstraint(kind="UNSUPPORTED", value="source requirement: " + text))
    updates["hard_constraints"] = tuple(dict.fromkeys(hard))
    updates["soft_constraints"] = tuple(
        dict.fromkeys(
            (
                *controls.soft_constraints,
                *(SoftConstraint(preference=value) for value in additions.preferences),
            )
        )
    )
    try:
        return ConstraintSet.model_validate({**controls.model_dump(), **updates})
    except ValidationError:
        return CompilationFailure(
            code="MODEL_OUTPUT_INVALID",
            message="Inferred additions conflict with the constraint contract",
        )


def parse_output(
    content: str,
    controls: ConstraintSet,
    text: str,
) -> ConstraintSet | CompilationFailure:
    def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate model output key")
            result[key] = value
        return result

    try:
        json.loads(content, object_pairs_hook=unique_object)
        result = merge_additions(controls, text, ParserAdditions.model_validate_json(content))
    except (ValidationError, ValueError):
        result = CompilationFailure(
            code="MODEL_OUTPUT_INVALID", message="Malformed parser output; requirements not relaxed"
        )
    protected = protected_requirements(text)
    if isinstance(result, CompilationFailure) and protected:
        return CompilationFailure(
            code=result.code,
            message=result.message
            + "; retained unsupported/needs evidence: "
            + ", ".join(protected)
            + "; source requirement: "
            + text,
        )
    return result


def model_request(controls: ConstraintSet, text: str, model: str) -> dict[str, object]:
    controls = ConstraintSet.model_validate(controls)
    root = Path(__file__).resolve().parents[3]
    prompt = (root / "prompts/parser.md").read_text(encoding="utf-8")
    schema = ParserAdditions.model_json_schema()
    for field in ("party_size", "max_walking_minutes", "max_walking_meters", "return_by_local"):
        if getattr(controls, field) is not None:
            schema["properties"][field]["const"] = None
    return {
        "model": model,
        "stream": False,
        "think": False,
        "format": schema,
        "messages": [
            {
                "role": "user",
                "content": prompt
                + "\nOutput JSON schema (vocabulary, not user requirements):\n"
                + json.dumps(schema)
                + "\nParse only this user sentence, empty/null for unmentioned concepts:\n"
                + json.dumps(
                    {
                        "unset_optional_controls": [
                            field
                            for field in (
                                "party_size",
                                "max_walking_minutes",
                                "max_walking_meters",
                                "return_by_local",
                            )
                            if getattr(controls, field) is None
                        ],
                        "sentence_to_parse": text,
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "options": {"temperature": 0, "seed": 42, "num_predict": 384, "num_ctx": 4096},
    }


def parse_constraints(
    controls: ConstraintSet,
    text: str,
    *,
    model: str,
    base_url: str = "http://127.0.0.1:11434",
    api_key: str | None = None,
) -> ConstraintSet | CompilationFailure:
    """One bounded local call. No retries, fallback model, or private prompt logging."""
    if len(text) > 4000:
        return CompilationFailure(
            code="UNSUPPORTED_CONSTRAINT", message="Free text exceeds 4000 characters"
        )
    base_url, headers = model_connection(base_url, api_key)
    try:
        with httpx.Client(timeout=120, trust_env=False) as client:
            response = client.post(
                base_url + "/api/chat",
                json=model_request(controls, text, model),
                headers=headers,
                follow_redirects=False,
            )
            response.raise_for_status()
            payload = response.json()
        if payload.get("done") is not True:
            raise ValueError("Incomplete model response")
        return parse_output(payload["message"]["content"], controls, text)
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return CompilationFailure(
            code="MODEL_OUTPUT_INVALID",
            message="Local parser failed; no constraints fabricated"
            + (
                "; retained unsupported/needs evidence: "
                + ", ".join(protected_requirements(text))
                + "; source requirement: "
                + text
                if protected_requirements(text)
                else ""
            ),
        )
