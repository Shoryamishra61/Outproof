import asyncio
import socket

import httpx
import pytest

from scripts.crawl_public_sources import PublicPage, crawl_site, relevant_links


def test_public_crawl_bounds_and_exclusions(monkeypatch) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("93.184.216.34", 443))],
    )
    page = PublicPage()
    page.feed('<script>fake ₹500</script><p>Restaurant</p><a href="/menu">Menu</a>')
    assert "fake" not in " ".join(page.words)
    assert relevant_links(
        "https://example.org/",
        ["//bad.example/menu", "/menu?token=secret", "/menu", "/about", "/contact"],
    ) == ["https://example.org/menu", "https://example.org/about"]
    calls = []

    def respond(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(200, text="User-agent: *\nDisallow: /")

    async def check() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            result = await crawl_site(client, "https://example.org/")
        assert result["pages"][0]["status"] == "ROBOTS_DISALLOWED"
        assert calls == ["/robots.txt"]

    asyncio.run(check())


@pytest.mark.parametrize(
    "address", ["127.0.0.1", "169.254.169.254", "10.0.0.1", "::1", "192.168.1.1"]
)
def test_crawler_rejects_private_resolution(monkeypatch, address):
    monkeypatch.setattr(
        socket, "getaddrinfo", lambda *args, **kwargs: [(None, None, None, None, (address, 443))]
    )

    async def check():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda r: pytest.fail("Private network request"))
        ) as client:
            result = await crawl_site(client, "https://example.org/")
            assert result["status"] == "ROBOTS_UNAVAILABLE"

    asyncio.run(check())


def test_crawler_does_not_follow_redirect_even_if_client_does(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("93.184.216.34", 443))],
    )
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(302, headers={"Location": "http://169.254.169.254/latest/meta-data"})

    async def check():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(respond), follow_redirects=True
        ) as client:
            assert (await crawl_site(client, "https://example.org/"))[
                "status"
            ] == "ROBOTS_UNAVAILABLE"
        assert len(calls) == 1
        assert calls[0].url.host == "93.184.216.34"
        assert calls[0].headers["Host"] == "example.org"
        assert calls[0].extensions["sni_hostname"] == "example.org"

    asyncio.run(check())
