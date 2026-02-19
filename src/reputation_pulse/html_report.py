from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

from reputation_pulse.charts import sparkline_svg


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
    sparkline = sparkline_svg(points)
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
