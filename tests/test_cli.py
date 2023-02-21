from patronload.cli import main


def test_cli_no_options(caplog, runner):
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=INFO" in caplog.text
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert "Total time to complete process" in caplog.text


def test_cli_log_configured_from_env(caplog, monkeypatch, runner):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=DEBUG" in caplog.text
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert "Total time to complete process" in caplog.text
