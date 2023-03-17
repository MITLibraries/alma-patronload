from patronload.s3 import delete_objects_from_bucket_with_prefix


def test_delete_objects_from_bucket_with_prefix_deletes_only_expected_objects(
    caplog, mocked_s3, s3_client
):
    assert len(mocked_s3.list_objects(Bucket="test-bucket")["Contents"]) == 2
    delete_objects_from_bucket_with_prefix(
        s3_client, ".zip", "test-bucket", "patronload"
    )
    assert (
        "'patronload/1.zip' deleted before processing new patron zip files"
        in caplog.text
    )
    assert s3_client.get_object(Bucket="test-bucket", Key="2.zip")
