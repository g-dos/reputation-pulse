from __future__ import annotations

from reputation_pulse.errors import InvalidHandleError


def normalize_handle(raw: str) -> str:
    normalized = raw.strip().lstrip("@")
    if not normalized:
        raise InvalidHandleError("Handle cannot be empty")
    return normalized
