from reputation_pulse.storage import ScanStore


def _sample_result(handle: str, score: float) -> dict[str, object]:
    return {
        "handle": handle,
        "github": {"followers": 1, "stars": 1, "recent_repos": []},
        "score": {"normalized": score},
        "summary": {"rating": "Needs Attention", "recommendations": []},
        "trend": {"direction": "new", "delta": 0.0},
    }


def test_store_save_and_latest_scans(tmp_path):
    db_path = tmp_path / "store.db"
    store = ScanStore(db_path=str(db_path))
    store.save_scan(_sample_result("g-dos", 12.0))
    store.save_scan(_sample_result("other", 20.0))

    rows = store.latest_scans(limit=2)
    assert len(rows) == 2
    assert rows[0]["handle"] == "other"


def test_store_latest_result_for_handle(tmp_path):
    db_path = tmp_path / "store.db"
    store = ScanStore(db_path=str(db_path))
    store.save_scan(_sample_result("g-dos", 12.0))
    store.save_scan(_sample_result("g-dos", 15.0))

    latest = store.latest_result_for_handle("g-dos")
    assert latest is not None
    assert latest["score"]["normalized"] == 15.0


def test_store_handle_insights(tmp_path):
    db_path = tmp_path / "store.db"
    store = ScanStore(db_path=str(db_path))
    store.save_scan(_sample_result("g-dos", 10.0))
    store.save_scan(_sample_result("g-dos", 20.0))

    insights = store.handle_insights("g-dos")
    assert insights is not None
    assert insights["scans_count"] == 2
    assert insights["average_score"] == 15.0
    assert insights["latest_score"] == 20.0
