import logging
from datetime import timedelta
from time import perf_counter

import click

from patronload.config import configure_logger, configure_sentry, load_config_values

logger = logging.getLogger(__name__)


@click.command()
def main() -> None:
    start_time = perf_counter()
    config_values = load_config_values()
    root_logger = logging.getLogger()
    log_level = config_values["LOG_LEVEL"] or "INFO"
    logger.info(configure_logger(root_logger, log_level))
    logger.info(configure_sentry())

    logger.info(
        "Patronload config settings loaded for environment: %s",
        config_values["WORKSPACE"],
    )
    logger.info("Running patronload process")

    # Do things here!

    elapsed_time = perf_counter() - start_time
    logger.info(
        "Total time to complete process: %s", str(timedelta(seconds=elapsed_time))
    )
