from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path


def _sparkline_svg(points: list[float]) -> str:
    if not points:
        return "<p>No history yet.</p>"
    if len(points) == 1:
        return "<p>Not enough history points for trend chart.</p>"

    width = 560
    height = 120
    padding = 12
    min_value = min(points)
    max_value = max(points)
    value_range = max(max_value - min_value, 1.0)
    step = (width - (padding * 2)) / (len(points) - 1)

    svg_points: list[str] = []
    for idx, value in enumerate(points):
        x = padding + (idx * step)
        normalized = (value - min_value) / value_range
        y = (height - padding) - (normalized * (height - (padding * 2)))
        svg_points.append(f"{x:.2f},{y:.2f}")

    polyline = " ".join(svg_points)
    min_text = (
        f'<text x="{padding}" y="{height - 2}" fill="#6b7280" '
        f'font-size="10">{min_value:.1f}</text>'
    )
    max_x = width - padding - 28
    max_text = (
        f'<text x="{max_x}" y="{height - 2}" fill="#6b7280" '
        f'font-size="10">{max_value:.1f}</text>'
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" height="{height}" '
        'role="img" aria-label="Score history chart">'
        f'<polyline fill="none" stroke="#2563eb" stroke-width="3" points="{polyline}" />'
        f"{min_text}"
        f"{max_text}"
        "</svg>"
    )


def render_html_report(
    result: dict[str, object],
    score_series: list[dict[str, object]] | None = None,
) -> str:
    handle = escape(str(result["handle"]))
    score = escape(str(result["score"]["normalized"]))
    rating = escape(str(result["summary"]["rating"]))
    trend = result.get("trend", {"direction": "unknown", "delta": 0.0})
    followers = escape(str(result["github"]["followers"]))
    stars = escape(str(result["github"]["stars"]))
    recommendations = result["summary"]["recommendations"]

    trend_direction = escape(str(trend["direction"]))
    trend_delta = escape(f"{float(trend['delta']):+}")
    rec_items = "".join(f"<li>{escape(str(item))}</li>" for item in recommendations)
    if not rec_items:
        rec_items = "<li>No recommendations.</li>"
    points = []
    if score_series:
        points = [float(item["normalized_score"]) for item in score_series]
    sparkline = _sparkline_svg(points)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Reputation Pulse Report - {handle}</title>
    <style>
      body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 2rem;
        color: #1f2937;
      }}
      .card {{
        border: 1px solid #d1d5db;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        max-width: 700px;
      }}
      h1 {{ margin-top: 0; }}
      .meta {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .5rem; }}
      .k {{ color: #6b7280; }}
      ul {{ margin-bottom: 0; }}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Reputation Pulse Report: {handle}</h1>
      <div class="meta">
        <div><span class="k">Score</span>: {score}</div>
        <div><span class="k">Rating</span>: {rating}</div>
        <div><span class="k">Trend</span>: {trend_direction} ({trend_delta})</div>
        <div><span class="k">Followers</span>: {followers}</div>
        <div><span class="k">Stars</span>: {stars}</div>
      </div>
      <h2>Recommendations</h2>
      <ul>{rec_items}</ul>
      <h2>Score History</h2>
      {sparkline}
    </div>
  </body>
</html>
"""


def write_html_report(
    result: dict[str, object],
    output_path: str,
    score_series: list[dict[str, object]] | None = None,
) -> str:
    html = render_html_report(result, score_series=score_series)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return str(path)


def default_report_path(handle: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"reports/{handle}-{timestamp}.html"
