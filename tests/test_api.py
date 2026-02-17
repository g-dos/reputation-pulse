from fastapi.testclient import TestClient

from reputation_pulse import api as api_module
from reputation_pulse.errors import (
    InvalidHandleError,
    UpstreamNotFoundError,
    UpstreamRateLimitError,
)

client = TestClient(api_module.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_scan_invalid_handle(monkeypatch):
    async def fake_run(_handle: str):
        raise InvalidHandleError("Handle cannot be empty")

    monkeypatch.setattr(api_module.analyzer, "run", fake_run)
    response = client.post("/scan", json={"handle": ""})
    assert response.status_code == 400


def test_scan_not_found(monkeypatch):
    async def fake_run(_handle: str):
        raise UpstreamNotFoundError("missing")

    monkeypatch.setattr(api_module.analyzer, "run", fake_run)
    response = client.post("/scan", json={"handle": "missing"})
    assert response.status_code == 404


def test_scan_rate_limit(monkeypatch):
    async def fake_run(_handle: str):
        raise UpstreamRateLimitError("limited")

    monkeypatch.setattr(api_module.analyzer, "run", fake_run)
    response = client.post("/scan", json={"handle": "g-dos"})
    assert response.status_code == 429


def test_scan_success_has_trend(monkeypatch):
    async def fake_run(_handle: str):
        return {
            "handle": "g-dos",
            "github": {"followers": 10, "stars": 5, "recent_repos": []},
            "score": {"normalized": 12.5},
            "summary": {"rating": "Needs Attention", "recommendations": []},
        }

    monkeypatch.setattr(api_module.analyzer, "run", fake_run)
    monkeypatch.setattr(
        api_module.store,
        "latest_scan_for_handle",
        lambda _handle: {"normalized_score": 10.0},
    )
    monkeypatch.setattr(api_module.store, "save_scan", lambda _result: None)
    response = client.post("/scan", json={"handle": "g-dos"})
    assert response.status_code == 200
    assert response.json()["trend"]["direction"] == "up"
