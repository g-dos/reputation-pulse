from __future__ import annotations

import asyncio
import json

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.errors import (
    CollectorError,
    InvalidHandleError,
    UpstreamNotFoundError,
    UpstreamRateLimitError,
)
from reputation_pulse.exporters import insights_to_csv, insights_to_json, write_export
from reputation_pulse.html_report import default_report_path, write_html_report
from reputation_pulse.scan_service import ScanService
from reputation_pulse.storage import ScanStore

app = typer.Typer(help="Reputation Pulse CLI")
console = Console()
analyzer = ReputationAnalyzer()
store = ScanStore()
scan_service = ScanService(analyzer=analyzer, store=store)


def _display_summary(result: dict[str, object]) -> None:
    score = result["score"]
    summary = result["summary"]
    trend = result["trend"]
    table = Table(title=f"Reputation Pulse: {result['handle']}", show_header=False)
    table.add_row("Normalized score", f"{score['normalized']} ({summary['rating']})")
    table.add_row("Trend", f"{trend['direction']} ({trend['delta']:+})")
    table.add_row("Followers", str(result["github"]["followers"]))
    table.add_row("Stars", str(result["github"]["stars"]))
    table.add_row("Recent repos", str(score["recent_repos"]))
    table.add_row("Recent web posts (30d)", str(result["web"]["recent_entries_30d"]))

    console.print(table)
    if summary["recommendations"]:
        console.print("\n[b]Recommendations[/b]")
        for item in summary["recommendations"]:
            console.print(f"- {item}")


@app.command()
def scan(
    handle: str,
    json_output: bool = typer.Option(False, "--json", help="Return raw JSON"),
) -> None:
    """Scan a public handle and report its reputation score."""
    try:
        result = asyncio.run(scan_service.run_and_store(handle))
    except InvalidHandleError as exc:
        console.print(f"[red]Invalid handle:[/red] {exc}")
        raise typer.Exit(code=2) from exc
    except UpstreamNotFoundError as exc:
        console.print(f"[red]Not found:[/red] {exc}")
        raise typer.Exit(code=3) from exc
    except UpstreamRateLimitError as exc:
        console.print(f"[red]Rate limit:[/red] {exc}")
        raise typer.Exit(code=4) from exc
    except CollectorError as exc:
        console.print(f"[red]Collector error:[/red] {exc}")
        raise typer.Exit(code=5) from exc

    if json_output:
        typer.echo(json.dumps(result, indent=2))
        return
    _display_summary(result)


@app.command()
def api(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Start the Reputation Pulse API."""
    console.print(f"Launching Reputation Pulse API on {host}:{port}")
    uvicorn.run("reputation_pulse.api:app", host=host, port=port, reload=reload)


@app.command()
def history(limit: int = typer.Option(10, min=1, max=100, help="Rows to show")) -> None:
    """Show the latest local scan history."""
    rows = store.latest_scans(limit=limit)
    table = Table(title="Latest Scans")
    table.add_column("Handle")
    table.add_column("Score")
    table.add_column("Rating")
    table.add_column("Scanned At (UTC)")
    for row in rows:
        table.add_row(
            str(row["handle"]),
            str(row["normalized_score"]),
            str(row["rating"]),
            str(row["scanned_at"]),
        )
    console.print(table)


@app.command()
def report(
    handle: str,
    output: str = typer.Option(
        "",
        "--output",
        help="Output HTML file path (defaults to handle + timestamp)",
    ),
) -> None:
    """Generate an HTML report from the latest stored scan for a handle."""
    normalized = handle.strip().lstrip("@")
    latest = store.latest_result_for_handle(normalized)
    if latest is None:
        console.print(f"No local scan found for '{normalized}'. Run scan first.")
        raise typer.Exit(code=1)
    report_path = output or default_report_path(normalized)
    series = store.score_series(normalized, limit=30)
    path = write_html_report(latest, report_path, score_series=series)
    console.print(f"Report written to {path}")


@app.command()
def insights(handle: str) -> None:
    """Show aggregated local insights for a handle."""
    normalized = handle.strip().lstrip("@")
    insight = store.handle_insights(normalized)
    if insight is None:
        console.print(f"No local scan found for '{normalized}'. Run scan first.")
        raise typer.Exit(code=1)

    table = Table(title=f"Insights: {normalized}", show_header=False)
    table.add_row("Scans", str(insight["scans_count"]))
    table.add_row("Average score", str(insight["average_score"]))
    table.add_row("Min score", str(insight["min_score"]))
    table.add_row("Max score", str(insight["max_score"]))
    table.add_row("Latest score", str(insight["latest_score"]))
    table.add_row("Latest rating", str(insight["latest_rating"]))
    table.add_row("First scan", str(insight["first_scan_at"]))
    table.add_row("Last scan", str(insight["last_scan_at"]))
    console.print(table)


@app.command("insights-export")
def insights_export(
    handle: str,
    format: str = typer.Option("json", "--format", help="json or csv"),
    output: str = typer.Option("", "--output", help="Output file path"),
) -> None:
    """Export aggregated insights to JSON or CSV."""
    normalized = handle.strip().lstrip("@")
    insight = store.handle_insights(normalized)
    if insight is None:
        console.print(f"No local scan found for '{normalized}'. Run scan first.")
        raise typer.Exit(code=1)

    export_format = format.strip().lower()
    if export_format not in {"json", "csv"}:
        console.print("Invalid format. Use --format json or --format csv.")
        raise typer.Exit(code=2)

    if export_format == "csv":
        content = insights_to_csv(insight)
        default_path = f"reports/{normalized}-insights.csv"
    else:
        content = insights_to_json(insight)
        default_path = f"reports/{normalized}-insights.json"

    target = output or default_path
    path = write_export(content, target)
    console.print(f"Insights exported to {path}")
