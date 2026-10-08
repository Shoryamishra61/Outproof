"""Explicit authenticated HTTPS hosting or the existing local Ollama path."""

import re
from urllib.parse import urlsplit


def model_connection(base_url: str, api_key: str | None = None) -> tuple[str, dict[str, str]]:
    if re.fullmatch(r"http://(?:127\.0\.0\.1|localhost|\[::1\]):\d+", base_url):
        return base_url, {}
    parsed = urlsplit(base_url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not api_key
        or "\n" in api_key
        or "\r" in api_key
    ):
        raise ValueError("Remote Gemma requires a configured HTTPS endpoint and authentication")
    return base_url.rstrip("/"), {"Authorization": f"Bearer {api_key}"}
