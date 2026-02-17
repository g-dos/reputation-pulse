import pytest

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.errors import InvalidHandleError


@pytest.mark.asyncio
async def test_analyzer_rejects_empty_handle():
    analyzer = ReputationAnalyzer()
    with pytest.raises(InvalidHandleError):
        await analyzer.run("   ")


@pytest.mark.asyncio
async def test_analyzer_includes_web_data():
    class FakeGitHub:
        async def collect(self, _handle: str):
            return {
                "handle": "g-dos",
                "followers": 10,
                "following": 1,
                "public_repos": 2,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "blog_url": "https://example.com/feed",
                "stars": 5,
                "recent_repos": [],
            }

    class FakeRss:
        async def collect(self, _blog_url: str):
            return {
                "blog_url": "https://example.com/feed",
                "feed_url": "https://example.com/feed",
                "recent_entries_30d": 2,
                "last_post_at": None,
            }

    analyzer = ReputationAnalyzer(github_collector=FakeGitHub(), rss_collector=FakeRss())
    result = await analyzer.run("g-dos")
    assert result["web"]["recent_entries_30d"] == 2
