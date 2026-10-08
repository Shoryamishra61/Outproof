"""Explicit bounded free-quota source discovery and noncommercial GO audio generation."""

import asyncio
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path

import httpx
from app.live import GATE, LivePlacesProvider
from app.source_discovery import SerpSourceDiscovery


async def main() -> None:
    async with httpx.AsyncClient(trust_env=False, timeout=60) as client:
        search = SerpSourceDiscovery(os.getenv("SERPAPI_API_KEY"))
        if search.key:
            result = await LivePlacesProvider(
                client, "https://overpass-api.de/api/interpreter", search
            ).discover(GATE, 1000)
            assert isinstance(result, tuple), "Official source unavailable"
            leads = [
                e.model_dump(mode="json")
                for e in result[0].evidence
                if e.field == "source_discovery"
            ]
            assert leads, "Official search result absent; no qualification claim"
            report = {
                "executed_at": datetime.now(UTC).isoformat(),
                "scope": "live search passed through independent authoritative normalizer",
                "leads": leads,
                "price_confidence": result[0].price.confidence.value,
            }
            Path("evals/reports/release-serpapi.json").write_text(
                json.dumps(report, indent=2) + "\n"
            )
            print("SerpApi discovery and authoritative normalization verified")
        audio_path = Path("apps/web/public/go-cue.mp3")
        key = os.getenv("ELEVENLABS_API_KEY")
        if key and not audio_path.exists():
            headers = {"xi-api-key": key}
            subscription = await client.get(
                "https://api.elevenlabs.io/v1/user/subscription", headers=headers
            )
            subscription.raise_for_status()
            limits = subscription.json()
            text = (
                "Your outing is checked. Open the walking map, "
                "follow the route to the garden entrance, "
                "and put your phone away when you are ready."
            )
            assert limits["tier"] == "free" and not limits["can_extend_character_limit"]
            assert limits["character_limit"] - limits["character_count"] >= len(text)
            voice = "EXAVITQu4vr4xnSDxMaL"
            response = await client.post(
                "https://api.elevenlabs.io/v1/text-to-speech/" + voice,
                headers=headers,
                params={"output_format": "mp3_44100_128"},
                json={"text": text, "model_id": "eleven_multilingual_v2"},
            )
            response.raise_for_status()
            assert response.headers.get("content-type", "").startswith("audio/")
            assert len(response.content) > 1000
            audio_path.write_bytes(response.content)
            report = {
                "executed_at": datetime.now(UTC).isoformat(),
                "http_status": response.status_code,
                "request_id": response.headers.get("request-id"),
                "voice": voice,
                "model": "eleven_multilingual_v2",
                "characters": len(text),
                "bytes": len(response.content),
                "sha256": hashlib.sha256(response.content).hexdigest(),
                "text": text,
                "license": "noncommercial free-tier demo; elevenlabs.io attribution",
            }
            Path("evals/reports/release-elevenlabs.json").write_text(
                json.dumps(report, indent=2) + "\n"
            )
            print("ElevenLabs actual GO cue generated")


if __name__ == "__main__":
    asyncio.run(main())
