import json
from pathlib import Path

import pytest
from ground_rule.models import CompilationFailure

from evals.runner import cached


@pytest.mark.parametrize("parser_fails", [False, True])
def test_cached_demo_fails_honestly_without_external_providers(
    tmp_path, monkeypatch, parser_fails
) -> None:
    def interpret(controls, text, *, model):
        return (
            CompilationFailure(code="MODEL_OUTPUT_INVALID", message="Synthetic test failure")
            if (parser_fails)
            else controls
        )

    monkeypatch.setattr(cached, "parse_constraints", interpret)
    paths = [
        Path("evals/reports") / name
        for name in [
            "discovery-chennai-live-1.json",
            "routing-chennai-live-1.json",
            "templates-chennai-real-data-1.json",
        ]
    ]
    originals = [p.read_bytes() for p in paths]
    report = cached.evaluate(*paths, "synthetic-no-model-call", tmp_path / "demo.json")
    assert report["external_discovery_or_routing_requests"] == 0
    assert report["accepted_outings"] == 0 and report["source_timestamps_refreshed"] is False
    assert report["authoritative_controls_preserved"] == (not parser_fails)
    assert report["enrichment_failure"]["code"] == "SOURCE_TEMPORARILY_UNAVAILABLE"
    assert [p.read_bytes() for p in paths] == originals
    assert json.loads((tmp_path / "demo.json").read_text(encoding="utf-8")) == report
    with pytest.raises(FileExistsError):
        cached.evaluate(*paths, "synthetic-no-model-call", tmp_path / "demo.json")
