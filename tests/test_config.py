import logging

import pytest

from patronload.config import (
    configure_logger,
    configure_sentry,
    create_log_stream_for_email,
    load_config_values,
)


def test_configure_logger_with_invalid_level_raises_error():
    logger = logging.getLogger(__name__)
    with pytest.raises(ValueError, match="'oops' is not a valid Python logging level"):
        configure_logger(logger, log_level_string="oops")


def test_configure_logger_info_level_or_higher():
    logger = logging.getLogger(__name__)
    result = configure_logger(logger, log_level_string="info")
    assert logger.getEffectiveLevel() == logging.INFO
    assert result == "Logger 'tests.test_config' configured with level=INFO"


def test_configure_logger_debug_level_or_lower():
    logger = logging.getLogger(__name__)
    result = configure_logger(logger, log_level_string="DEBUG")
    assert logger.getEffectiveLevel() == logging.DEBUG
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


def test_create_log_stream_for_email_success(caplog):
    caplog.set_level("DEBUG")
    stream = create_log_stream_for_email(logging.getLogger())
    assert "Log stream handler configured" in stream.getvalue()


def test_load_config_values_success():
    config_values = load_config_values()
    assert config_values == {
        "USER": "user123",
        "PASSWORD": "pass123",
        "HOST": "http://localhost",
        "PORT": "1234",
        "PATH": "database5678",
        "S3_BUCKET_NAME": "test-bucket",
        "S3_PREFIX": "patronload",
        "SES_RECIPIENT_EMAIL": "to@example.com",
        "SES_SEND_FROM_EMAIL": "from@example.com",
        "WORKSPACE": "test",
    }


def load_config_values_missing_variable_raises_error(
    monkeypatch,
):
    monkeypatch.delenv("WORKSPACE", raising=False)
    with pytest.raises(KeyError):
        load_config_values()
