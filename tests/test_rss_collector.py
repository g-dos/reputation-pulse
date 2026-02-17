from datetime import datetime, timedelta, timezone

import pytest

import reputation_pulse.collectors.rss as rss_module
from reputation_pulse.collectors.rss import RssCollector


class FakeResponse:
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class FakeClient:
    def __init__(self, responses):
        self.responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def get(self, *_args, **_kwargs):
        return self.responses.pop(0)


@pytest.mark.asyncio
async def test_rss_collector_parses_recent_entries(monkeypatch):
    now = datetime.now(timezone.utc)
    recent = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
    old = (now - timedelta(days=120)).strftime("%a, %d %b %Y %H:%M:%S GMT")
    xml = (
        "<rss><channel>"
        f"<item><pubDate>{recent}</pubDate></item>"
        f"<item><pubDate>{old}</pubDate></item>"
        "</channel></rss>"
    )
    monkeypatch.setattr(
        rss_module.httpx,
        "AsyncClient",
        lambda **_kwargs: FakeClient([FakeResponse(200, xml)]),
    )
    result = await RssCollector().collect("https://example.com/feed")
    assert result["recent_entries_30d"] == 1
    assert result["feed_url"] == "https://example.com/feed"


@pytest.mark.asyncio
async def test_rss_collector_handles_missing_feed(monkeypatch):
    monkeypatch.setattr(
        rss_module.httpx,
        "AsyncClient",
        lambda **_kwargs: FakeClient([FakeResponse(404, "missing")] * 5),
    )
    result = await RssCollector().collect("https://example.com")
    assert result["recent_entries_30d"] == 0
    assert result["feed_url"] == ""
