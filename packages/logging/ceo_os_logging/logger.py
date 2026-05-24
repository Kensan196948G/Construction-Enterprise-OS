"""CEO-OS unified logging configuration.

Provides structured JSON logging via structlog for all services.
Usage:
    from ceo_os_logging import get_logger
    logger = get_logger(__name__)
    logger.info("user.login", user_id="xxx", ip="1.2.3.4")
"""

import logging
import structlog


def setup_logging(
    service_name: str = "ceo-os",
    log_level: str = "INFO",
) -> structlog.BoundLogger:
    """Configure structured logging for a service.

    Args:
        service_name: Name of the service (e.g. "auth", "gateway")
        log_level: Minimum log level

    Returns:
        Configured structlog logger
    """
    # Common processors for all services
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        structlog.dev.ConsoleRenderer() if log_level == "DEBUG"
        else structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Set root logger level
    logging.getLogger().setLevel(getattr(logging, log_level.upper()))

    return structlog.get_logger(service_name=service_name)


def get_logger(name: str = "ceo-os") -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging to any class."""

    @property
    def logger(self) -> structlog.BoundLogger:
        return structlog.get_logger(self.__class__.__name__)
