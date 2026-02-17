from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.errors import (
    CollectorError,
    InvalidHandleError,
    UpstreamNotFoundError,
    UpstreamRateLimitError,
)
from reputation_pulse.storage import ScanStore

app = FastAPI(title="Reputation Pulse API", version="0.1.0")
analyzer = ReputationAnalyzer()
store = ScanStore()


class ScanRequest(BaseModel):
    handle: str


@app.get("/health", summary="Basic health check")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scan", summary="Analyze a public handle")
async def scan(request: ScanRequest) -> dict[str, object]:
    try:
        result = await analyzer.run(request.handle)
        store.save_scan(result)
        return result
    except InvalidHandleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UpstreamNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except UpstreamRateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except CollectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/history", summary="Get latest scans")
async def history(limit: int = 10) -> dict[str, object]:
    return {"items": store.latest_scans(limit=max(1, min(limit, 100)))}
