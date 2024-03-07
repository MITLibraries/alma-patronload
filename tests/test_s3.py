import logging

from patronload.s3 import delete_zip_files_from_bucket_with_prefix


def test_delete_zip_files_from_bucket_with_prefix_deletes_only_expected_objects(
    caplog, mocked_s3, s3_client
):
    caplog.set_level(logging.DEBUG)
    assert (
        len(mocked_s3.list_objects(Bucket="test-bucket")["Contents"])
        == 2  # noqa: PLR2004
    )
    delete_zip_files_from_bucket_with_prefix(s3_client, "test-bucket", "patronload")
    assert (
        "'patronload/1.zip' deleted before processing new patron zip files" in caplog.text
    )
    assert s3_client.get_object(Bucket="test-bucket", Key="2.zip")
    assert len(mocked_s3.list_objects(Bucket="test-bucket")["Contents"]) == 1


def test_delete_zip_files_from_bucket_with_prefix_nonexistent_prefix_no_objects_deleted(
    mocked_s3, s3_client
):
    assert (
        len(mocked_s3.list_objects(Bucket="test-bucket")["Contents"])
        == 2  # noqa: PLR2004
    )
    delete_zip_files_from_bucket_with_prefix(s3_client, "test-bucket", "notaprefix")
    assert (
        len(mocked_s3.list_objects(Bucket="test-bucket")["Contents"])
        == 2  # noqa: PLR2004
    )
