from typer.testing import CliRunner

import reputation_pulse.cli as cli_module
from reputation_pulse.errors import InvalidHandleError

runner = CliRunner()


def test_cli_scan_invalid_handle(monkeypatch):
    async def fake_run(_handle: str):
        raise InvalidHandleError("Handle cannot be empty")

    monkeypatch.setattr(cli_module.analyzer, "run", fake_run)
    result = runner.invoke(cli_module.app, ["scan", ""])
    assert result.exit_code == 2
    assert "Invalid handle" in result.stdout


def test_cli_report_requires_existing_scan(monkeypatch):
    monkeypatch.setattr(cli_module.store, "latest_result_for_handle", lambda _handle: None)
    result = runner.invoke(cli_module.app, ["report", "missing"])
    assert result.exit_code == 1
    assert "No local scan found" in result.stdout


def test_cli_insights_requires_existing_scan(monkeypatch):
    monkeypatch.setattr(cli_module.store, "handle_insights", lambda _handle: None)
    result = runner.invoke(cli_module.app, ["insights", "missing"])
    assert result.exit_code == 1
    assert "No local scan found" in result.stdout
