from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile

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


@patch("patronload.database.oracledb")
@patch("patronload.cli.client")
def test_cli_database_connection_success(
    mocked_cli_client,
    mocked_oracledb,
    caplog,
    runner,
):
    mocked_oracledb.connect.return_value.version = 12.34
    result = runner.invoke(main, ["-t"])
    assert result.exit_code == 0
    assert "Patronload config settings loaded for environment: test" in caplog.text
    assert "Running patronload process" in caplog.text
    assert "Successfully connected to Oracle Database version: 12.34" in caplog.text
    mocked_cli_client.assert_not_called()


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


@freeze_time("2023-03-01 12:00:00")
@patch("patronload.database.oracledb")
def test_cli_duplicate_krb_name_remains_staff_patron(
    mocked_oracledb,
    mocked_s3,  # pylint: disable=W0613
    runner,
    s3_client,
    staff_database_record_with_all_values,
):
    mocked_oracledb.connect.return_value.cursor.return_value.fetchall.side_effect = [
        [
            staff_database_record_with_all_values,
        ],
        [
            (
                "111111111",
                None,
                "STAFF_KRB_NAME",
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        ],
    ]
    runner.invoke(main)
    staff_zip_file = s3_client.get_object(
        Bucket="test-bucket",
        Key="patronload/staff_2023-03-01_12.00.00.zip",
    )
    with ZipFile(BytesIO(staff_zip_file["Body"].read()), "r") as zip_file:
        assert "STAFF_KRB_NAME" in zip_file.read(
            "staff_2023-03-01_12.00.00.xml"
        ).decode("utf-8")

    student_zip_file = s3_client.get_object(
        Bucket="test-bucket",
        Key="patronload/student_2023-03-01_12.00.00.zip",
    )
    with ZipFile(BytesIO(student_zip_file["Body"].read()), "r") as zip_file:
        assert "STAFF_KRB_NAME" not in zip_file.read(
            "student_2023-03-01_12.00.00.xml"
        ).decode("utf-8")
