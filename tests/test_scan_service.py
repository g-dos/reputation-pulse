import pytest

from reputation_pulse.scan_service import ScanService


class DummyAnalyzer:
    async def run(self, _handle: str) -> dict[str, object]:
        return {
            "handle": "g-dos",
            "github": {"followers": 10, "stars": 5, "recent_repos": []},
            "score": {"normalized": 20.0},
            "summary": {"rating": "Needs Attention", "recommendations": []},
        }


class DummyStore:
    def __init__(self) -> None:
        self.saved = None

    def latest_scan_for_handle(self, _handle: str):
        return {"normalized_score": 10.0}

    def save_scan(self, result: dict[str, object]) -> None:
        self.saved = result


@pytest.mark.asyncio
async def test_scan_service_adds_trend_and_saves():
    store = DummyStore()
    service = ScanService(analyzer=DummyAnalyzer(), store=store)
    result = await service.run_and_store("g-dos")
    assert result["trend"]["direction"] == "up"
    assert store.saved is not None
