import logging
import os
from datetime import datetime, timedelta
from io import BytesIO
from time import perf_counter
from zipfile import ZipFile

import click
from boto3 import client

from patronload.config import (
    STAFF_FIELDS,
    STUDENT_FIELDS,
    configure_logger,
    configure_sentry,
    load_config_values,
)
from patronload.database import (
    build_sql_query,
    create_database_connection,
    query_database,
)
from patronload.patron import patrons_xml_string_from_records

logger = logging.getLogger(__name__)


@click.command()
def main() -> None:
    start_time = perf_counter()
    config_values = load_config_values()
    root_logger = logging.getLogger()
    logger.info(configure_logger(root_logger, os.getenv("LOG_LEVEL", "INFO")))
    logger.info(configure_sentry())

    logger.info(
        "Patronload config settings loaded for environment: %s",
        config_values["WORKSPACE"],
    )
    logger.info("Running patronload process")

    connection = create_database_connection(config_values)
    logger.info(
        "Successfully connected to Oracle Database version : %s", connection.version
    )

    s3_client = client("s3")
    for zip_file_key in [
        s3_object["Key"]
        for s3_object in s3_client.list_objects(
            Bucket=config_values["S3_BUCKET_NAME"], Prefix=config_values["S3_PATH"]
        )["Contents"]
        if s3_object["Key"].endswith(".zip")
    ]:
        s3_client.delete_object(
            Bucket=config_values["S3_BUCKET_NAME"], Key=zip_file_key
        )

    existing_ids: list[str] = []
    for patron_type, query_params in {
        "staff": {"fields": STAFF_FIELDS, "table": "LIBRARY_EMPLOYEE"},
        "student": {"fields": STUDENT_FIELDS, "table": "LIBRARY_STUDENT"},
    }.items():
        query = build_sql_query(
            list(query_params["fields"]), str(query_params["table"])
        )
        patron_records = query_database(connection, query)
        logger.info(
            "'%s' patron records retrieved from Data Warehouse", len(patron_records)
        )

        file_name = f"{patron_type}_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
        zip_file_object = BytesIO()
        with ZipFile(zip_file_object, "a") as zip_file:
            zip_file.writestr(
                f"{file_name}.xml",
                patrons_xml_string_from_records(
                    patron_type, patron_records, existing_ids
                ),
            )
        logger.info("XML data created and zipped for %s patrons ", patron_type)
        s3_client.put_object(
            Body=zip_file_object.getvalue(),
            Bucket=config_values["S3_BUCKET_NAME"],
            Key=f"{config_values['S3_PATH']}/{file_name}.zip",
        )
        logger.info(
            "'%s' uploaded to S3 bucket '%s'",
            file_name + ".zip",
            config_values["S3_BUCKET_NAME"],
        )

    elapsed_time = perf_counter() - start_time
    logger.info(
        "Total time to complete process: %s", str(timedelta(seconds=elapsed_time))
    )
