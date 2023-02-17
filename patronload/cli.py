import logging
from datetime import timedelta
from time import perf_counter

import click

from patronload.config import configure_logger, configure_sentry, load_config_values

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-v", "--verbose", is_flag=True, help="Pass to log at debug level instead of info"
)
def main(verbose: bool) -> None:
    start_time = perf_counter()
    root_logger = logging.getLogger()
    logger.info(configure_logger(root_logger, verbose))
    config_values = load_config_values()
    logger.info(
        configure_sentry(config_values["WORKSPACE"], config_values["SENTRY_DSN"])
    )

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
