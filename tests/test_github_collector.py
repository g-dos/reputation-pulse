import pytest

import reputation_pulse.collectors.github as github_module
from reputation_pulse.collectors.github import GitHubCollector
from reputation_pulse.errors import UpstreamNotFoundError, UpstreamRateLimitError


class FakeResponse:
    def __init__(self, status_code: int, payload: object):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


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
async def test_collect_success(monkeypatch):
    responses = [
        FakeResponse(200, {"followers": 10, "following": 1, "public_repos": 2}),
        FakeResponse(
            200,
            [
                {"name": "b", "pushed_at": "2024-01-02T00:00:00Z", "stargazers_count": 5},
                {"name": "a", "pushed_at": "2024-01-03T00:00:00Z", "stargazers_count": 7},
            ],
        ),
    ]
    monkeypatch.setattr(github_module.httpx, "AsyncClient", lambda **_kwargs: FakeClient(responses))

    result = await GitHubCollector().collect("g-dos")
    assert result["followers"] == 10
    assert result["stars"] == 12
    assert result["recent_repos"][0]["name"] == "a"


@pytest.mark.asyncio
async def test_collect_not_found(monkeypatch):
    responses = [FakeResponse(404, {}), FakeResponse(200, [])]
    monkeypatch.setattr(github_module.httpx, "AsyncClient", lambda **_kwargs: FakeClient(responses))

    with pytest.raises(UpstreamNotFoundError):
        await GitHubCollector().collect("missing")


@pytest.mark.asyncio
async def test_collect_rate_limited(monkeypatch):
    responses = [FakeResponse(403, {}), FakeResponse(200, [])]
    monkeypatch.setattr(github_module.httpx, "AsyncClient", lambda **_kwargs: FakeClient(responses))

    with pytest.raises(UpstreamRateLimitError):
        await GitHubCollector().collect("g-dos")
