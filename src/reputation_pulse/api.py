from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.errors import (
    CollectorError,
    InvalidHandleError,
    UpstreamNotFoundError,
    UpstreamRateLimitError,
)
from reputation_pulse.exporters import insights_to_csv, insights_to_json
from reputation_pulse.handles import normalize_handle
from reputation_pulse.html_report import render_html_report
from reputation_pulse.models import ScanRequest
from reputation_pulse.scan_service import ScanService
from reputation_pulse.storage import ScanStore

app = FastAPI(title="Reputation Pulse API", version="0.1.0")
store = ScanStore()
scan_service = ScanService(analyzer=ReputationAnalyzer(), store=store)


def _normalize_or_400(handle: str) -> str:
    try:
        return normalize_handle(handle)
    except InvalidHandleError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/health", summary="Basic health check")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scan", summary="Analyze a public handle")
async def scan(request: ScanRequest) -> dict[str, object]:
    try:
        return await scan_service.run_and_store(request.handle)
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
async def history(limit: int = Query(default=10, ge=1, le=100)) -> dict[str, object]:
    return {"items": store.latest_scans(limit=limit)}


@app.get("/report/{handle}", response_class=HTMLResponse, summary="Get latest scan as HTML report")
async def report(handle: str) -> HTMLResponse:
    normalized = _normalize_or_400(handle)
    latest = store.latest_result_for_handle(normalized)
    if latest is None:
        raise HTTPException(status_code=404, detail="No scan history for this handle")
    series = store.score_series(normalized, limit=30)
    return HTMLResponse(content=render_html_report(latest, score_series=series))


@app.get("/insights/{handle}", summary="Get aggregated insights for a handle")
async def insights(handle: str) -> dict[str, object]:
    normalized = _normalize_or_400(handle)
    insight = store.handle_insights(normalized)
    if insight is None:
        raise HTTPException(status_code=404, detail="No scan history for this handle")
    return insight


@app.get("/series/{handle}", summary="Get score time series for a handle")
async def series(
    handle: str,
    limit: int = Query(default=30, ge=1, le=365),
) -> dict[str, object]:
    normalized = _normalize_or_400(handle)
    points = store.score_series(normalized, limit=limit)
    if not points:
        raise HTTPException(status_code=404, detail="No scan history for this handle")
    return {"handle": normalized, "items": points}


@app.get("/insights/{handle}/export", summary="Export insights in CSV or JSON")
async def insights_export(
    handle: str,
    format: str = Query(default="json", pattern="^(json|csv)$"),
) -> Response:
    normalized = _normalize_or_400(handle)
    insight = store.handle_insights(normalized)
    if insight is None:
        raise HTTPException(status_code=404, detail="No scan history for this handle")
    if format == "csv":
        return Response(
            content=insights_to_csv(insight),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{normalized}-insights.csv"'},
        )
    return Response(
        content=insights_to_json(insight),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{normalized}-insights.json"'},
    )
