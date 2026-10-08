import asyncio
from datetime import UTC, datetime

import httpx
import pytest
from app.live import LivePlacesProvider, normalize_tanglin
from ground_rule.models import CompilationFailure

GATE = {
    "elements": [
        {
            "type": "node",
            "id": 602215681,
            "lat": 1.3071437,
            "lon": 103.8185997,
            "tags": {"name": "Tanglin Gate", "barrier": "gate", "foot": "yes"},
        }
    ]
}
# Synthetic excerpt exercises the parser; it is not a cached live observation.
HTML = (
    "<p>The Gardens is free entry for everyone, everyday.</p><h2>Gardens</h2>"
    "<p>5am to 12mn daily</p><p>Tanglin Entrance is served by Napier &amp; Holland Road.</p>"
)


@pytest.mark.parametrize("kind", ["price", "hours", "gate", "hidden", "moved", "identity"])
def test_changed_or_hidden_source_never_establishes_operational_fact(kind: str) -> None:
    from copy import deepcopy

    gate, html = deepcopy(GATE), HTML
    if kind in {"price", "hours", "gate"}:
        html = html.replace(
            {"price": "free entry", "hours": "5am", "gate": "Tanglin"}[kind], "changed"
        )
    elif kind == "hidden":
        html = "<script>" + html + "</script>"
    elif kind == "moved":
        gate["elements"][0]["lat"] = 13.0
    else:
        gate["elements"][0]["id"] = 1
    with pytest.raises(ValueError):
        normalize_tanglin(gate, html, datetime.now(UTC))


def test_no_timestamp_refresh_or_scope_expansion() -> None:
    observed = datetime(2026, 10, 8, tzinfo=UTC)
    place = normalize_tanglin(GATE, HTML, observed)
    assert place.price.upper.currency_code == "SGD" and place.price.upper.minor_units == 0
    assert all(e.observed_at == observed and e.expires_at is not None for e in place.evidence)
    assert not any(e.field == "excluded_categories" for e in place.evidence)
    assert "No National Orchid Garden" in next(
        e.value for e in place.evidence if e.field == "visit_scope"
    )


@pytest.mark.parametrize("status", [301, 401, 403, 404, 429, 500, 502, 503, 504])
def test_fixed_source_errors_fail_closed_without_redirects(status: int) -> None:
    calls = []

    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request.url)
        return httpx.Response(status, headers={"Location": "http://169.254.169.254/"})

    async def run() -> None:
        from app.live import GATE as coords

        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handle), follow_redirects=True
        ) as client:
            result = await LivePlacesProvider(client, "https://example.org").discover(coords, 1000)
        assert isinstance(result, CompilationFailure) and len(calls) == 1

    asyncio.run(run())
