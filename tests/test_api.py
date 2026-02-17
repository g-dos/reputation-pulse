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
    async def fake_scan(_handle: str):
        raise InvalidHandleError("Handle cannot be empty")

    monkeypatch.setattr(api_module.scan_service, "run_and_store", fake_scan)
    response = client.post("/scan", json={"handle": "g-dos"})
    assert response.status_code == 400


def test_scan_rejects_blank_handle():
    response = client.post("/scan", json={"handle": "   "})
    assert response.status_code == 422


def test_scan_not_found(monkeypatch):
    async def fake_scan(_handle: str):
        raise UpstreamNotFoundError("missing")

    monkeypatch.setattr(api_module.scan_service, "run_and_store", fake_scan)
    response = client.post("/scan", json={"handle": "missing"})
    assert response.status_code == 404


def test_scan_rate_limit(monkeypatch):
    async def fake_scan(_handle: str):
        raise UpstreamRateLimitError("limited")

    monkeypatch.setattr(api_module.scan_service, "run_and_store", fake_scan)
    response = client.post("/scan", json={"handle": "g-dos"})
    assert response.status_code == 429


def test_scan_success_has_trend(monkeypatch):
    async def fake_scan(_handle: str):
        return {
            "handle": "g-dos",
            "github": {"followers": 10, "stars": 5, "recent_repos": []},
            "score": {"normalized": 12.5},
            "summary": {"rating": "Needs Attention", "recommendations": []},
            "trend": {"direction": "up", "delta": 2.5},
        }

    monkeypatch.setattr(api_module.scan_service, "run_and_store", fake_scan)
    response = client.post("/scan", json={"handle": "g-dos"})
    assert response.status_code == 200
    assert response.json()["trend"]["direction"] == "up"


def test_report_404_when_missing(monkeypatch):
    monkeypatch.setattr(api_module.store, "latest_result_for_handle", lambda _handle: None)
    response = client.get("/report/missing")
    assert response.status_code == 404


def test_report_returns_html(monkeypatch):
    monkeypatch.setattr(
        api_module.store,
        "latest_result_for_handle",
        lambda _handle: {
            "handle": "g-dos",
            "github": {"followers": 1, "stars": 2},
            "score": {"normalized": 10.0},
            "summary": {"rating": "Needs Attention", "recommendations": []},
            "trend": {"direction": "new", "delta": 0.0},
        },
    )
    response = client.get("/report/g-dos")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_insights_404_when_missing(monkeypatch):
    monkeypatch.setattr(api_module.store, "handle_insights", lambda _handle: None)
    response = client.get("/insights/missing")
    assert response.status_code == 404


def test_insights_success(monkeypatch):
    monkeypatch.setattr(
        api_module.store,
        "handle_insights",
        lambda _handle: {
            "handle": "g-dos",
            "scans_count": 3,
            "average_score": 20.0,
            "min_score": 10.0,
            "max_score": 30.0,
            "first_scan_at": "2026-01-01T00:00:00+00:00",
            "last_scan_at": "2026-01-02T00:00:00+00:00",
            "latest_score": 30.0,
            "latest_rating": "Stable",
        },
    )
    response = client.get("/insights/g-dos")
    assert response.status_code == 200
    assert response.json()["scans_count"] == 3
