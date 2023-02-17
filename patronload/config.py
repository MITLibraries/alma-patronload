import logging
import os
from typing import Optional

import sentry_sdk

EXPECTED_CONFIG_VARIABLES = [
    "DATA_WAREHOUSE_USER",
    "DATA_WAREHOUSE_PASSWORD",
    "DATA_WAREHOUSE_HOST",
    "DATA_WAREHOUSE_PORT",
    "DATA_WAREHOUSE_SID",
    "LOG_LEVEL",
    "S3_BUCKET_NAME",
    "S3_PATH",
    "SENTRY_DSN",
    "WORKSPACE",
]


def configure_logger(logger: logging.Logger, verbose: bool) -> str:
    if verbose:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s() line %(lineno)d: "
            "%(message)s"
        )
        logger.setLevel(logging.DEBUG)
        for handler in logging.root.handlers:
            handler.addFilter(logging.Filter("patronload"))
    else:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s(): %(message)s"
        )
        logger.setLevel(logging.INFO)
    return (
        f"Logger '{logger.name}' configured with level="
        f"{logging.getLevelName(logger.getEffectiveLevel())}"
    )


def configure_sentry(env: str, sentry_dsn: str) -> str:
    if sentry_dsn and sentry_dsn.lower() != "none":
        sentry_sdk.init(sentry_dsn, environment=env)
        return f"Sentry DSN found, exceptions will be sent to Sentry with env={env}"
    return "No Sentry DSN found, exceptions will not be sent to Sentry"


def load_config_values() -> dict:
    """
    Retrieve all required env variables and return as a dict.

    If an env variable is not present, a KeyError will be raised by the
    get_required_env_variable function with a reminder that it is required
    by the application.
    """
    config_values = {}
    for expected_config_variable in EXPECTED_CONFIG_VARIABLES:
        if config_value := get_required_env_variable(expected_config_variable):
            config_values[expected_config_variable] = config_value
    return config_values


def get_required_env_variable(variable_name: str) -> Optional[str]:
    try:
        return os.environ[variable_name]
    except KeyError as error:
        raise KeyError(
            f"Missing variable: '{variable_name}' is required for all environments"
        ) from error
