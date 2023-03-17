import logging

logger = logging.getLogger(__name__)


def delete_objects_from_bucket_with_prefix(  # type: ignore
    s3_client,
    file_extension: str,
    s3_bucket_name: str,
    s3_prefix: str,
) -> None:
    """
    Delete S3 objects with the specified prefix from the specified bucket.

    Args:
        s3_client: A configured s3 client.
        file_extension: The file extension of the objects to be deleted.
        s3_bucket_name: The bucket containing the objects to be deleted.
        s3_prefix: The prefix of the keys of the objects to be deleted.
    """
    for file_to_delete_key in [
        s3_object["Key"]
        for s3_object in s3_client.list_objects(
            Bucket=s3_bucket_name, Prefix=s3_prefix
        )["Contents"]
        if s3_object["Key"].endswith(file_extension)
    ]:
        s3_client.delete_object(Bucket=s3_bucket_name, Key=file_to_delete_key)
        logger.debug(
            "'%s' deleted before processing new patron zip files", file_to_delete_key
        )
