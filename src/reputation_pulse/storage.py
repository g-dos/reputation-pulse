from __future__ import annotations

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from reputation_pulse.settings import settings


class ScanStore:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or settings.db_path
        self._ensure_schema()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    handle TEXT NOT NULL,
                    normalized_score REAL NOT NULL,
                    rating TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    scanned_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_scan(self, result: dict[str, object]) -> None:
        scanned_at = datetime.now(timezone.utc).isoformat()
        payload = json.dumps(result)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO scans (handle, normalized_score, rating, payload, scanned_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(result["handle"]),
                    float(result["score"]["normalized"]),
                    str(result["summary"]["rating"]),
                    payload,
                    scanned_at,
                ),
            )
            conn.commit()

    def latest_scans(self, limit: int = 10) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT handle, normalized_score, rating, scanned_at
                FROM scans
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "handle": row[0],
                "normalized_score": row[1],
                "rating": row[2],
                "scanned_at": row[3],
            }
            for row in rows
        ]

    def latest_scan_for_handle(self, handle: str) -> dict[str, object] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT handle, normalized_score, rating, scanned_at
                FROM scans
                WHERE handle = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (handle,),
            ).fetchone()

        if row is None:
            return None

        return {
            "handle": row[0],
            "normalized_score": row[1],
            "rating": row[2],
            "scanned_at": row[3],
        }

    def latest_result_for_handle(self, handle: str) -> dict[str, object] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT payload
                FROM scans
                WHERE handle = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (handle,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])
