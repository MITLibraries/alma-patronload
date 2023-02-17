import logging

import pytest

from patronload.config import (
    configure_logger,
    configure_sentry,
    get_required_env_variable,
    load_config_values,
)


def test_configure_logger_not_verbose():
    logger = logging.getLogger(__name__)
    result = configure_logger(logger, verbose=False)
    assert logger.getEffectiveLevel() == 20
    assert result == "Logger 'tests.test_config' configured with level=INFO"


def test_configure_logger_verbose():
    logger = logging.getLogger(__name__)
    result = configure_logger(logger, verbose=True)
    assert logger.getEffectiveLevel() == 10
    assert result == "Logger 'tests.test_config' configured with level=DEBUG"


def test_configure_sentry_env_variable_is_none():
    result = configure_sentry("test", None)
    assert result == "No Sentry DSN found, exceptions will not be sent to Sentry"


def test_configure_sentry_env_variable_is_dsn():
    result = configure_sentry(
        "test", "https://1234567890@00000.ingest.sentry.io/123456"
    )
    assert result == "Sentry DSN found, exceptions will be sent to Sentry with env=test"


def test_config_get_required_env_variable_success():
    assert get_required_env_variable("WORKSPACE") == "test"


def test_config_get_required_env_variable_missing_variable_raises_error(
    monkeypatch,
):
    with pytest.raises(KeyError):
        monkeypatch.delenv("WORKSPACE", raising=False)
        get_required_env_variable("WORKSPACE")


def test_load_config_values_success():
    config_values = load_config_values()
    assert config_values == {
        "DATA_WAREHOUSE_USER": "user123",
        "DATA_WAREHOUSE_PASSWORD": "pass123",
        "DATA_WAREHOUSE_HOST": "http://localhost",
        "DATA_WAREHOUSE_PORT": "1234",
        "DATA_WAREHOUSE_SID": "database5678",
        "LOG_LEVEL": "INFO",
        "S3_BUCKET_NAME": "patronload",
        "S3_PATH": "/test/example/",
        "SENTRY_DSN": "https://1234567890@00000.ingest.sentry.io/123456",
        "WORKSPACE": "test",
    }


def load_config_values_missing_variable_raises_error(
    monkeypatch,
):
    with pytest.raises(KeyError):
        monkeypatch.delenv("WORKSPACE", raising=False)
        load_config_values()
