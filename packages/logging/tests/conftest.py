"""Pytest fixtures for logging tests."""

import logging
import pytest
import structlog


@pytest.fixture(autouse=True)
def reset_structlog():
    """Reset structlog configuration before each test."""
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()
    logging.getLogger().setLevel(logging.INFO)
    yield
    structlog.reset_defaults()
    logging.getLogger().handlers.clear()
    logging.getLogger().setLevel(logging.INFO)
