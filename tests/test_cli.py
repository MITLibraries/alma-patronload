from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile

from freezegun import freeze_time

from patronload.cli import main


@freeze_time("2023-03-01")
@patch("patronload.database.oracledb")
def test_cli_no_options(
    mocked_oracledb, caplog, mocked_s3, runner, s3_client  # pylint: disable=W0613
):
    assert "Contents" not in mocked_s3.list_objects(Bucket="test-bucket")
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=INFO" in caplog.text
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert "'staff_2023-03-01.zip' uploaded to S3 bucket 'test-bucket'" in caplog.text
    assert "'student_2023-03-01.zip' uploaded to S3 bucket 'test-bucket'" in caplog.text
    s3_bucket_contents = mocked_s3.list_objects(Bucket="test-bucket")["Contents"]
    assert s3_bucket_contents[0]["Key"] == "patronload/staff_2023-03-01.zip"
    assert s3_bucket_contents[1]["Key"] == "patronload/student_2023-03-01.zip"
    for file_name in ["staff_2023-03-01", "student_2023-03-01"]:
        zip_file = s3_client.get_object(
            Bucket="test-bucket",
            Key=f"patronload/{file_name}.zip",
        )
        with ZipFile(BytesIO(zip_file["Body"].read()), "r") as zip_file:
            assert zip_file.namelist() == [file_name + ".xml"]
    assert "Total time to complete process" in caplog.text


@freeze_time("2023-03-01")
@patch("patronload.database.oracledb")
def test_cli_log_configured_from_env(  # pylint: disable=R0913
    mocked_oracledb,  # pylint: disable=W0613
    caplog,
    mocked_s3,
    monkeypatch,
    runner,
    s3_client,
):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    assert "Contents" not in mocked_s3.list_objects(Bucket="test-bucket")
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "Logger 'root' configured with level=DEBUG" in caplog.text
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert "'staff_2023-03-01.zip' uploaded to S3 bucket 'test-bucket'" in caplog.text
    assert "'student_2023-03-01.zip' uploaded to S3 bucket 'test-bucket'" in caplog.text
    s3_bucket_contents = mocked_s3.list_objects(Bucket="test-bucket")["Contents"]
    assert s3_bucket_contents[0]["Key"] == "patronload/staff_2023-03-01.zip"
    assert s3_bucket_contents[1]["Key"] == "patronload/student_2023-03-01.zip"
    for file_name in ["staff_2023-03-01", "student_2023-03-01"]:
        zip_file = s3_client.get_object(
            Bucket="test-bucket",
            Key=f"patronload/{file_name}.zip",
        )
        with ZipFile(BytesIO(zip_file["Body"].read()), "r") as zip_file:
            assert zip_file.namelist() == [file_name + ".xml"]
    assert "Total time to complete process" in caplog.text
