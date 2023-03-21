import logging

from mypy_boto3_s3 import S3Client

logger = logging.getLogger(__name__)


def delete_zip_files_from_bucket_with_prefix(
    s3_client: S3Client,
    s3_bucket_name: str,
    s3_prefix: str,
) -> None:
    """
    Delete zip file objects with the specified prefix from the specified bucket.

    Args:
        s3_client: A configured s3 client.
        s3_bucket_name: The bucket containing the objects to be deleted.
        s3_prefix: The prefix of the keys of the objects to be deleted.
    """
    s3_objects_with_prefix = s3_client.list_objects_v2(
        Bucket=s3_bucket_name, Prefix=s3_prefix
    )
    if "Contents" in s3_objects_with_prefix:
        for object_to_delete_key in [
            s3_object["Key"]
            for s3_object in s3_objects_with_prefix["Contents"]
            if s3_object["Key"].endswith(".zip")
        ]:
            s3_client.delete_object(Bucket=s3_bucket_name, Key=object_to_delete_key)
            logger.debug(
                "'%s' deleted before processing new patron zip files",
                object_to_delete_key,
            )
