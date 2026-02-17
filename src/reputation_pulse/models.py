from __future__ import annotations

from pydantic import BaseModel, field_validator


class ScanRequest(BaseModel):
    handle: str

    @field_validator("handle")
    @classmethod
    def normalize_handle(cls, value: str) -> str:
        normalized = value.strip().lstrip("@")
        if not normalized:
            raise ValueError("Handle cannot be empty")
        return normalized
