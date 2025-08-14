from typer.testing import CliRunner

from cli import app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Coinbase Advanced Bot runners" in result.output
