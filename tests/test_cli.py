from unittest.mock import patch

from freezegun import freeze_time

from patronload.cli import main


@patch("patronload.database.oracledb")
def test_cli_log_configured_from_env(
    mocked_oracledb,  # pylint: disable=W0613
    caplog,
    monkeypatch,
    mocked_s3,  # pylint: disable=W0613
    runner,
):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=DEBUG" in caplog.text


@freeze_time("2023-03-01 12:00:00")
@patch("patronload.database.oracledb")
def test_cli_success(
    mocked_oracledb,  # pylint: disable=W0613
    caplog,
    mocked_s3,
    runner,
):
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=INFO" in caplog.text
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert (
        "'staff_2023-03-01_12.00.00.zip' uploaded to S3 bucket 'test-bucket'"
        in caplog.text
    )
    assert (
        "'student_2023-03-01_12.00.00.zip' uploaded to S3 bucket 'test-bucket'"
        in caplog.text
    )
    s3_bucket_path_contents = mocked_s3.list_objects_v2(
        Bucket="test-bucket", Prefix="patronload"
    )["Contents"]
    assert (
        s3_bucket_path_contents[0]["Key"] == "patronload/staff_2023-03-01_12.00.00.zip"
    )
    assert (
        s3_bucket_path_contents[1]["Key"]
        == "patronload/student_2023-03-01_12.00.00.zip"
    )
    assert "Total time to complete process" in caplog.text
