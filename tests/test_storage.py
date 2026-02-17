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


def test_store_latest_result_handles_corrupt_payload(tmp_path):
    db_path = tmp_path / "store.db"
    store = ScanStore(db_path=str(db_path))
    with store._connect() as conn:  # noqa: SLF001 - intentional white-box test
        conn.execute(
            """
            INSERT INTO scans (handle, normalized_score, rating, payload, scanned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("g-dos", 10.0, "Stable", "{bad", "2026-01-01T00:00:00+00:00"),
        )
        conn.commit()

    latest = store.latest_result_for_handle("g-dos")
    assert latest is None


def test_store_score_series_orders_oldest_to_newest(tmp_path):
    db_path = tmp_path / "store.db"
    store = ScanStore(db_path=str(db_path))
    store.save_scan(_sample_result("g-dos", 10.0))
    store.save_scan(_sample_result("g-dos", 20.0))
    store.save_scan(_sample_result("g-dos", 30.0))

    series = store.score_series("g-dos", limit=2)
    assert len(series) == 2
    assert series[0]["normalized_score"] == 20.0
    assert series[1]["normalized_score"] == 30.0
