"""
Datetime utilities for timezone-aware operations.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Returns the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def iso_now() -> str:
    """Returns ISO 8601 formatted string of current UTC datetime."""
    return utc_now().isoformat()
