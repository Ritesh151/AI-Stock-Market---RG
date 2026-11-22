"""
Structured Logging Configuration for RG AI.
Provides clean logging formats and scrubs sensitive data.
"""

import logging
import sys
import re
from typing import Any, Dict


SENSITIVE_PATTERNS = [
    re.compile(r"(mongodb(\+srv)?://)[^:@]+:[^@]+@", re.IGNORECASE),
    re.compile(r"(bearer\s+)[a-zA-Z0-9_\-\.]+", re.IGNORECASE),
    re.compile(r"(password|secret|token|api_key)\s*[:=]\s*['\"]?[^\s'\"]+", re.IGNORECASE),
]


def sanitize_log_message(message: str) -> str:
    """
    Scrubs credentials and secrets from log messages.
    """
    for pattern in SENSITIVE_PATTERNS:
        message = pattern.sub(r"\1[REDACTED]@", message)
    return message


class SafeFormatter(logging.Formatter):
    """
    Custom log formatter that ensures sensitive secrets are never logged.
    """

    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return sanitize_log_message(original)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Initializes and configures the root application logger.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    root_logger = logging.getLogger("rg_ai")
    root_logger.setLevel(level)

    # Clear existing handlers to prevent duplicate lines
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    format_str = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d]: %(message)s"
    formatter = SafeFormatter(format_str, datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.propagate = False

    return root_logger


def get_logger(name: str = "rg_ai") -> logging.Logger:
    """
    Retrieves a named child logger under the rg_ai namespace.
    """
    if name == "rg_ai":
        return logging.getLogger("rg_ai")
    return logging.getLogger(f"rg_ai.{name}")
