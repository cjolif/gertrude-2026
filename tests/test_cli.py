"""Tests for the CLI."""

from typer.testing import CliRunner

from gertrude.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "gertrude 0.1.0" in result.stdout


def test_chat_help() -> None:
    result = runner.invoke(app, ["chat", "--help"])
    assert result.exit_code == 0
    assert "Start an interactive chat session" in result.stdout
    assert "--model" in result.stdout
