import json
import logging
import os
from io import StringIO

import sentry_sdk

STAFF_FIELDS = [
    "MIT_ID",
    "EMAIL_ADDRESS",
    "KRB_NAME_UPPERCASE",
    "LIBRARY_ID",
    "FULL_NAME",
    "OFFICE_ADDRESS",
    "OFFICE_PHONE",
    "APPOINTMENT_END_DATE",
    "LIBRARY_PERSON_TYPE_CODE",
    "LIBRARY_PERSON_TYPE",
    "ORG_UNIT_ID",
    "ORG_UNIT_TITLE",
    "POSITION_TITLE",
    "DIRECTORY_TITLE",
]

STUDENT_FIELDS = [
    "MIT_ID",
    "EMAIL_ADDRESS",
    "KRB_NAME_UPPERCASE",
    "LIBRARY_ID",
    "LAST_NAME",
    "FIRST_NAME",
    "MIDDLE_NAME",
    "TERM_STREET1",
    "TERM_STREET2",
    "TERM_CITY",
    "TERM_STATE",
    "TERM_ZIP",
    "TERM_PHONE1",
    "TERM_PHONE2",
    "OFFICE_PHONE",
    "STUDENT_YEAR",
    "HOME_DEPARTMENT",
]

with open("config/staff_departments.txt", encoding="utf8") as txt_file:
    STAFF_DEPARTMENTS: dict[str, str] = json.load(txt_file)

with open("config/student_departments.txt", encoding="utf8") as txt_file:
    STUDENT_DEPARTMENTS: dict[str, str] = json.load(txt_file)


def configure_logger(logger: logging.Logger, log_level_string: str) -> str:
    if log_level_string.upper() not in logging.getLevelNamesMapping():
        message = f"'{log_level_string}' is not a valid Python logging level"
        raise ValueError(message)
    log_level = logging.getLevelName(log_level_string.upper())
    if log_level < logging.INFO:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s() line %(lineno)d: "
            "%(message)s"
        )
        logger.setLevel(log_level)
        for handler in logging.root.handlers:
            handler.addFilter(logging.Filter("patronload"))
    else:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s(): %(message)s"
        )
        logger.setLevel(log_level)
    return (
        f"Logger '{logger.name}' configured with level="
        f"{logging.getLevelName(logger.getEffectiveLevel())}"
    )


def configure_sentry() -> str:
    env = os.getenv("WORKSPACE")
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn and sentry_dsn.lower() != "none":
        sentry_sdk.init(sentry_dsn, environment=env)
        return f"Sentry DSN found, exceptions will be sent to Sentry with env={env}"
    return "No Sentry DSN found, exceptions will not be sent to Sentry"


def create_log_stream_for_email(logger: logging.Logger) -> StringIO:
    """Create log stream for populating email notification.

    Args:
        logger: The root logger to be configured with the stream handler.
    """
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.debug("Log stream handler configured")
    return stream


def load_config_values() -> dict:
    """Retrieve all required env variables to update the config_values dict."""
    config_values = {}
    for config_variable in [
        "S3_BUCKET_NAME",
        "S3_PREFIX",
        "WORKSPACE",
        "SES_RECIPIENT_EMAIL",
        "SES_SEND_FROM_EMAIL",
    ]:
        config_values[config_variable] = os.environ[config_variable]
    config_values.update(json.loads(os.environ["DATAWAREHOUSE_CLOUDCONNECTOR_JSON"]))
    return config_values
