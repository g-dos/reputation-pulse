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
