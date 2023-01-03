from my_app.cli import main


def test_cli_no_options(caplog, runner):
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=INFO" in caplog.text
    assert "Running process" in caplog.text
    assert "Total time to complete process" in caplog.text


def test_cli_all_options(caplog, runner):
    result = runner.invoke(main, ["--verbose"])
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=DEBUG" in caplog.text
    assert "Running process" in caplog.text
    assert "Total time to complete process" in caplog.text
