from unittest.mock import patch

from patronload.cli import main


@patch("patronload.database.oracledb")
def test_cli_no_options(mocked_oracledb, caplog, runner):  # pylint: disable=W0613
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=INFO" in caplog.text
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert "Total time to complete process" in caplog.text


@patch("patronload.database.oracledb")
def test_cli_log_configured_from_env(
    mocked_oracledb, caplog, monkeypatch, runner  # pylint: disable=W0613
):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=DEBUG" in caplog.text
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert "Total time to complete process" in caplog.text
