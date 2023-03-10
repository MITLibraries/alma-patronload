import logging

import pytest

from patronload.config import configure_logger, configure_sentry, load_config_values


def test_configure_logger_with_invalid_level_raises_error():
    logger = logging.getLogger(__name__)
    with pytest.raises(ValueError) as error:
        configure_logger(logger, log_level_string="oops")
    assert "'oops' is not a valid Python logging level" in str(error)


def test_configure_logger_info_level_or_higher():
    logger = logging.getLogger(__name__)
    result = configure_logger(logger, log_level_string="info")
    assert logger.getEffectiveLevel() == 20
    assert result == "Logger 'tests.test_config' configured with level=INFO"


def test_configure_logger_debug_level_or_lower():
    logger = logging.getLogger(__name__)
    result = configure_logger(logger, log_level_string="DEBUG")
    assert logger.getEffectiveLevel() == 10
    assert result == "Logger 'tests.test_config' configured with level=DEBUG"


def test_configure_sentry_no_env_variable(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    result = configure_sentry()
    assert result == "No Sentry DSN found, exceptions will not be sent to Sentry"


def test_configure_sentry_env_variable_is_none(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "None")
    result = configure_sentry()
    assert result == "No Sentry DSN found, exceptions will not be sent to Sentry"


def test_configure_sentry_env_variable_is_dsn(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://1234567890@00000.ingest.sentry.io/123456")
    result = configure_sentry()
    assert result == "Sentry DSN found, exceptions will be sent to Sentry with env=test"


def test_load_config_values_success():
    config_values = load_config_values()
    assert config_values == {
        "DATAWAREHOUSE_CLOUDCONNECTOR_JSON": (
            '{"USER": "user123",  "PASSWORD": "pass123", "HOST": "http://localhost", '
            '"PORT": "1234", "PATH": "database5678"}'
        ),
        "S3_BUCKET_NAME": "patronload",
        "S3_PATH": "/test/example/",
        "WORKSPACE": "test",
    }


def load_config_values_missing_variable_raises_error(
    monkeypatch,
):
    with pytest.raises(KeyError):
        monkeypatch.delenv("WORKSPACE", raising=False)
        load_config_values()
