from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from reputation_pulse.settings import settings


class CacheStore:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir or settings.cache_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _file(self, key: str) -> Path:
        safe_key = key.replace("/", "_").replace(":", "_")
        return self.base_dir / f"{safe_key}.json"

    def get(self, key: str, ttl_seconds: int) -> dict[str, object] | None:
        path = self._file(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        stored_at = datetime.fromisoformat(payload["stored_at"])
        if datetime.now(timezone.utc) - stored_at > timedelta(seconds=ttl_seconds):
            return None
        return payload["data"]

    def set(self, key: str, data: dict[str, object]) -> None:
        path = self._file(key)
        payload = {
            "stored_at": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
