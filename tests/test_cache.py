import json
from datetime import datetime, timedelta, timezone

from reputation_pulse.cache import CacheStore


def test_cache_store_get_set(tmp_path):
    cache = CacheStore(base_dir=str(tmp_path))
    cache.set("github:g-dos", {"value": 1})
    payload = cache.get("github:g-dos", ttl_seconds=60)
    assert payload == {"value": 1}


def test_cache_store_expires_entry(tmp_path):
    cache = CacheStore(base_dir=str(tmp_path))
    path = tmp_path / "github_g-dos.json"
    stale_payload = {
        "stored_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        "data": {"value": 1},
    }
    path.write_text(json.dumps(stale_payload), encoding="utf-8")
    payload = cache.get("github:g-dos", ttl_seconds=60)
    assert payload is None
