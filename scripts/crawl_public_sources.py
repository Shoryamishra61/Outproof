"""Bounded public-site lead collection. Output is never operational policy evidence."""

import argparse
import asyncio
import hashlib
import ipaddress
import json
import re
import socket
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

import httpx

AGENT = "GroundRuleEvidenceProbe"
MAX_BYTES = 1_000_000


async def public_request(client: httpx.AsyncClient, url: str) -> httpx.Request:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.port not in {None, 443}
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Public HTTPS URL without credentials required")
    addresses = await asyncio.to_thread(
        socket.getaddrinfo, parsed.hostname, 443, type=socket.SOCK_STREAM
    )
    ips = {row[4][0] for row in addresses}
    if not ips or any(not ipaddress.ip_address(ip).is_global for ip in ips):
        raise ValueError("Private or reserved address rejected")
    # Pin the validated IP; TLS still verifies the original hostname, preventing DNS rebinding.
    request = client.build_request("GET", httpx.URL(url).copy_with(host=sorted(ips)[0]), timeout=10)
    request.headers["Host"] = parsed.hostname
    request.extensions["sni_hostname"] = parsed.hostname
    return request


class PublicPage(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.words: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag == "a" and (href := dict(attrs).get("href")):
            self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, text: str) -> None:
        if not self.hidden:
            self.words.append(text)


def same_site(first: str, second: str) -> bool:
    return (urlsplit(first).hostname or "").removeprefix("www.") == (
        urlsplit(second).hostname or ""
    ).removeprefix("www.")


def relevant_links(root: str, links: list[str]) -> list[str]:
    result = []
    for href in links:
        url = urljoin(root, href).split("#")[0]
        parsed = urlsplit(url)
        if (
            parsed.scheme in {"http", "https"}
            and same_site(root, url)
            and not parsed.query
            and re.search(r"menu|contact|location|restaurant|about|dining", parsed.path, re.I)
            and url not in result
            and url != root
        ):
            result.append(url)
    return result[:2]


async def crawl_site(client: httpx.AsyncClient, root: str) -> dict[str, object]:
    parsed = urlsplit(root)
    robot_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    records: list[dict[str, object]] = []
    try:
        robots = await client.send(await public_request(client, robot_url), follow_redirects=False)
        if len(robots.content) > MAX_BYTES:
            raise ValueError("Robots size bound exceeded")
        if robots.status_code not in {200, 404}:
            return {"root": root, "status": "ROBOTS_UNAVAILABLE", "http_status": robots.status_code}
        rules = RobotFileParser()
        rules.parse(robots.text.splitlines() if robots.status_code == 200 else [])
        delay = rules.crawl_delay(AGENT) or rules.crawl_delay("*") or 0
        if delay > 5:
            return {"root": root, "status": "CRAWL_DELAY_EXCEEDS_PROBE_BOUND"}
        queue = [root]
        for url in queue:
            if not rules.can_fetch(AGENT, url):
                records.append({"source_ref": url, "status": "ROBOTS_DISALLOWED"})
                continue
            if delay:
                await asyncio.sleep(delay)
            record: dict[str, object] = {"source_ref": url}
            try:
                response = await client.send(
                    await public_request(client, url), stream=True, follow_redirects=False
                )
                try:
                    record.update(
                        http_status=response.status_code,
                        final_url=url,
                        observed_at=datetime.now(UTC).isoformat(),
                    )
                    if response.is_redirect:
                        record["status"] = "REDIRECT_REJECTED"
                    elif response.status_code != 200:
                        record["status"] = "HTTP_UNAVAILABLE"
                    else:
                        body = bytearray()
                        async for chunk in response.aiter_bytes():
                            body.extend(chunk)
                            if len(body) > MAX_BYTES:
                                raise ValueError("Response size bound exceeded")
                        record.update(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
                        if "text/html" in response.headers.get("content-type", ""):
                            page = PublicPage()
                            page.feed(body.decode(response.encoding or "utf-8", errors="replace"))
                            text = " ".join(page.words)
                            record.update(
                                status="HTML_LEADS_ONLY",
                                numeric_currency_signal=bool(re.search(r"₹|Rs\.?|INR", text)),
                                tax_charge_signal=bool(re.search(r"tax|charge", text, re.I)),
                                hours_signal=bool(
                                    re.search(r"opening|timings|hours|[ap]\.?m", text, re.I)
                                ),
                                vegetarian_signal=bool(
                                    re.search(r"vegetarian|pure veg", text, re.I)
                                ),
                            )
                            if url == root:
                                queue.extend(relevant_links(url, page.links))
                        else:
                            record["status"] = "DOCUMENT_NEEDS_REVIEW"
                finally:
                    await response.aclose()
            except (httpx.HTTPError, ValueError) as error:
                record.update(status="UNAVAILABLE", failure_type=type(error).__name__)
            records.append(record)
        return {"root": root, "robots_status": robots.status_code, "pages": records}
    except (httpx.HTTPError, ValueError, OSError) as error:
        return {"root": root, "status": "ROBOTS_UNAVAILABLE", "failure_type": type(error).__name__}


async def run(roots: list[str]) -> dict[str, object]:
    async with httpx.AsyncClient(
        headers={"User-Agent": AGENT}, trust_env=False, follow_redirects=False
    ) as client:
        # ponytail: serial, at most 3 pages/site; only parallelize if measured latency warrants it.
        sites = [await crawl_site(client, root) for root in roots]
    return {
        "scope": "PUBLIC_CRAWL_LEADS_ONLY_NOT_POLICY_EVIDENCE",
        "executed_at": datetime.now(UTC).isoformat(),
        "limits": {"sites": len(roots), "pages_per_site": 3, "bytes_per_page": MAX_BYTES},
        "sites": sites,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or len(args.url) > 12:
        raise SystemExit("Refusing observation overwrite or more than 12 sites")
    if any(
        urlsplit(u).scheme not in {"http", "https"} or not urlsplit(u).hostname for u in args.url
    ):
        raise SystemExit("Public HTTP(S) URLs required")
    report = asyncio.run(run(args.url))
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sites": len(report["sites"]), "artifact": str(args.output)}))
