"""Optional search leads; snippets never establish operational venue facts."""

import asyncio
from datetime import UTC, datetime, timedelta

import httpx

OFFICIAL_URL = "https://sbg.nparks.gov.sg/visit/general-info/"


def official_leads(payload: dict) -> list[str]:
    return sorted(
        {
            row["link"]
            for row in payload.get("organic_results", [])
            if isinstance(row, dict)
            and row.get("link")
            in {OFFICIAL_URL, "https://sbg.nparks.gov.sg/", "https://sbg.nparks.gov.sg/visit/"}
        }
    )


class SerpSourceDiscovery:
    def __init__(self, key: str | None):
        self.key = key
        self.observed_at: datetime | None = None
        self.links: list[str] = []
        self.lock = asyncio.Lock()

    async def search(self, client: httpx.AsyncClient) -> tuple[list[str], datetime | None]:
        if not self.key:
            return [], None
        async with self.lock:
            if self.observed_at and datetime.now(UTC) - self.observed_at < timedelta(days=1):
                return self.links, self.observed_at
            try:
                response = await client.get(
                    "https://serpapi.com/search.json",
                    params={
                        "api_key": self.key,
                        "engine": "google",
                        "num": 5,
                        "q": 'site:sbg.nparks.gov.sg "General Info"',
                    },
                    timeout=15,
                    follow_redirects=False,
                )
                response.raise_for_status()
                self.links = official_leads(response.json())
                self.observed_at = datetime.now(UTC)
            except (httpx.HTTPError, ValueError, KeyError, TypeError):
                return [], None
            return self.links, self.observed_at
