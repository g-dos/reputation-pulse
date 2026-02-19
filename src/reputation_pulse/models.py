from __future__ import annotations

from pydantic import BaseModel, field_validator

from reputation_pulse.errors import InvalidHandleError
from reputation_pulse.handles import normalize_handle


class ScanRequest(BaseModel):
    handle: str

    @field_validator("handle")
    @classmethod
    def normalize_handle(cls, value: str) -> str:
        try:
            return normalize_handle(value)
        except InvalidHandleError as exc:
            raise ValueError(str(exc)) from exc
