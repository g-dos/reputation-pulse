from __future__ import annotations

import asyncio
import json

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from reputation_pulse.analyzer import ReputationAnalyzer
from reputation_pulse.storage import ScanStore

app = typer.Typer(help="Reputation Pulse CLI")
console = Console()
analyzer = ReputationAnalyzer()
store = ScanStore()


def _display_summary(result: dict[str, object]) -> None:
    score = result["score"]
    summary = result["summary"]
    table = Table(title=f"Reputation Pulse: {result['handle']}", show_header=False)
    table.add_row("Normalized score", f"{score['normalized']} ({summary['rating']})")
    table.add_row("Followers", str(result["github"]["followers"]))
    table.add_row("Stars", str(result["github"]["stars"]))
    table.add_row("Recent repos", str(score["recent_repos"]))

    console.print(table)
    if summary["recommendations"]:
        console.print("\n[b]Recommendations[/b]")
        for item in summary["recommendations"]:
            console.print(f"- {item}")


@app.command()
def scan(handle: str, json_output: bool = typer.Option(False, "--json", help="Return raw JSON")) -> None:
    """Scan a public handle and report its reputation score."""
    result = asyncio.run(analyzer.run(handle))
    store.save_scan(result)
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
