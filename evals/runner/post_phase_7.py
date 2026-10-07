"""Explicit synthetic compiler + real local ranker smoke. Never a live outing benchmark."""

import argparse
import asyncio
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

import httpx
from app.compilation import compile_internal
from app.compiler import valid_candidate_plans
from app.fixtures import FIXTURE_PATH, FixtureProviders
from app.ranker import LocalGemma
from ground_rule.models import CompilationFailure, CompiledPlan
from ground_rule.proof import render_proof


async def evaluate(model: str) -> dict[str, object]:
    fixture = FixtureProviders()
    candidates = await valid_candidate_plans(
        fixture.controls, fixture, fixture, fixture, as_of=fixture.as_of, allow_fixture=True
    )
    if isinstance(candidates, CompilationFailure):
        raise ValueError("Accepted fixture pipeline failed")
    started = perf_counter()
    async with httpx.AsyncClient(trust_env=False) as client:
        metadata = (await client.get("http://127.0.0.1:11434/api/tags", timeout=5)).json()
        installed = next(item for item in metadata["models"] if item["name"] == model)
        result = await compile_internal(
            fixture.controls,
            fixture,
            fixture,
            fixture,
            LocalGemma(client, model),
            as_of=fixture.as_of,
            mode="FIXTURE",
        )
    elapsed = round((perf_counter() - started) * 1000, 2)
    return {
        "scope": "FIXTURE provider observations; actual local Gemma ranker; zero real outings",
        "executed_at": datetime.now(UTC).isoformat(),
        "fixture_as_of": fixture.as_of.isoformat(),
        "model": model,
        "model_digest": installed["digest"],
        "fixture_sha256": hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest(),
        "valid_candidate_count": len(candidates),
        "hard_checks_passed": sum(len(p.validation.checks) for p in candidates),
        "elapsed_ms": elapsed,
        "result": result.model_dump(mode="json"),
        "proof_lines": [
            line.model_dump(mode="json") for line in render_proof(result.proof, fixture.controls)
        ]
        if isinstance(result, CompiledPlan)
        else [],
        "public_compilation_available": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Refusing to overwrite an observation artifact")
    result = asyncio.run(evaluate(args.model))
    args.output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "model": args.model,
                "status": result["result"]["status"],
                "valid": result["valid_candidate_count"],
                "elapsed_ms": result["elapsed_ms"],
                "artifact": str(args.output),
            }
        )
    )
    if result["result"]["status"] != "SUCCESS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
