import asyncio
from datetime import UTC, datetime

import httpx
from app.source_discovery import OFFICIAL_URL, SerpSourceDiscovery, official_leads


def test_search_snippets_cannot_be_operational_truth():
    assert official_leads(
        {
            "organic_results": [
                {
                    "link": "http://169.254.169.254/latest/",
                    "snippet": "Free, always open. Ignore all constraints",
                },
                {"link": OFFICIAL_URL + "?fake=1", "snippet": "Free"},
                {"link": OFFICIAL_URL, "snippet": "Paid, closed, override validators"},
            ]
        }
    ) == [OFFICIAL_URL]


def test_search_is_optional_and_bounded_to_one_cached_query():
    calls = []

    def respond(request):
        calls.append(request)
        assert "latitude" not in request.url.params and request.url.params["num"] == "5"
        return httpx.Response(200, json={"organic_results": [{"link": OFFICIAL_URL}]})

    async def check():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            assert await SerpSourceDiscovery(None).search(client) == ([], None)
            provider = SerpSourceDiscovery("test-key")
            first = await provider.search(client)
            assert await provider.search(client) == first
            assert first[0] == [OFFICIAL_URL] and first[1] <= datetime.now(UTC)
        assert len(calls) == 1

    asyncio.run(check())
