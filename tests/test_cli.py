from typer.testing import CliRunner

import reputation_pulse.cli as cli_module
from reputation_pulse.errors import InvalidHandleError

runner = CliRunner()


def test_cli_scan_invalid_handle(monkeypatch):
    async def fake_run(_handle: str):
        raise InvalidHandleError("Handle cannot be empty")

    monkeypatch.setattr(cli_module.scan_service, "run_and_store", fake_run)
    result = runner.invoke(cli_module.app, ["scan", ""])
    assert result.exit_code == 2
    assert "Invalid handle" in result.stdout


def test_cli_report_requires_existing_scan(monkeypatch):
    monkeypatch.setattr(cli_module.store, "latest_result_for_handle", lambda _handle: None)
    result = runner.invoke(cli_module.app, ["report", "missing"])
    assert result.exit_code == 1
    assert "No local scan found" in result.stdout


def test_cli_report_invalid_handle():
    result = runner.invoke(cli_module.app, ["report", "   "])
    assert result.exit_code == 2
    assert "Invalid handle" in result.stdout


def test_cli_insights_requires_existing_scan(monkeypatch):
    monkeypatch.setattr(cli_module.store, "handle_insights", lambda _handle: None)
    result = runner.invoke(cli_module.app, ["insights", "missing"])
    assert result.exit_code == 1
    assert "No local scan found" in result.stdout


def test_cli_report_uses_default_path(monkeypatch):
    monkeypatch.setattr(
        cli_module.store,
        "latest_result_for_handle",
        lambda _handle: {
            "handle": "g-dos",
            "github": {"followers": 1, "stars": 2},
            "score": {"normalized": 10.0},
            "summary": {"rating": "Needs Attention", "recommendations": []},
            "trend": {"direction": "new", "delta": 0.0},
        },
    )
    monkeypatch.setattr(cli_module, "default_report_path", lambda _handle: "reports/default.html")
    monkeypatch.setattr(
        cli_module,
        "write_html_report",
        lambda _latest, _path, score_series=None: _path,
    )
    result = runner.invoke(cli_module.app, ["report", "g-dos"])
    assert result.exit_code == 0
    assert "reports/default.html" in result.stdout


def test_cli_insights_export_json(monkeypatch):
    monkeypatch.setattr(
        cli_module.store,
        "handle_insights",
        lambda _handle: {"handle": "g-dos", "scans_count": 2},
    )
    monkeypatch.setattr(cli_module, "write_export", lambda _content, path: path)
    result = runner.invoke(cli_module.app, ["insights-export", "g-dos", "--format", "json"])
    assert result.exit_code == 0
    assert "g-dos-insights.json" in result.stdout


def test_cli_insights_export_invalid_format(monkeypatch):
    monkeypatch.setattr(
        cli_module.store,
        "handle_insights",
        lambda _handle: {"handle": "g-dos", "scans_count": 2},
    )
    result = runner.invoke(cli_module.app, ["insights-export", "g-dos", "--format", "xml"])
    assert result.exit_code == 2


def test_cli_series_json(monkeypatch):
    points = [{"normalized_score": 10.0, "scanned_at": "2026-01-01T00:00:00+00:00"}]
    monkeypatch.setattr(
        cli_module.store,
        "score_series",
        lambda _handle, limit=30: points,
    )
    result = runner.invoke(cli_module.app, ["series", "g-dos", "--json"])
    assert result.exit_code == 0
    assert '"handle": "g-dos"' in result.stdout
