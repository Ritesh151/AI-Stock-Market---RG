"""
Abstract and Concrete Asynchronous Base Repository for MongoDB.
Provides safe, sanitized MongoDB document operations using PyMongo Async API.
"""

from abc import ABC, abstractmethod
import re
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pymongo.asynchronous.collection import AsyncCollection
from pydantic import BaseModel

from app.core.database import get_database_manager
from app.core.logging import get_logger

logger = get_logger("repository")
T = TypeVar("T", bound=BaseModel)

# Dangerous MongoDB operators that must never be accepted from external parameters
_DANGEROUS_OPERATORS = {
    "$where",
    "$function",
    "$accumulator",
    "$expr",
    "$lookup",
    "$graphLookup",
    "$merge",
    "$out",
}


def sanitize_filter(filter_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitizes database query filters to prevent NoSQL operator injection and arbitrary script execution.
    """
    sanitized: Dict[str, Any] = {}
    for k, v in filter_dict.items():
        if k in _DANGEROUS_OPERATORS or k.startswith("$where") or k.startswith("$func"):
            logger.warning(f"Rejected dangerous MongoDB query operator: {k}")
            continue
        if isinstance(k, str) and "\x00" in k:
            logger.warning("Rejected null byte in query key")
            continue
        if isinstance(v, dict):
            sanitized[k] = sanitize_filter(v)
        elif isinstance(v, list):
            sanitized[k] = [
                sanitize_filter(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            sanitized[k] = v
    return sanitized



class BaseRepository(ABC, Generic[T]):
    """
    Abstract contract for collection-level persistence operations.
    """

    def __init__(self, collection_name: str):
        self._collection_name = collection_name

    @property
    def collection(self) -> Optional[AsyncCollection]:
        """Provides access to the active AsyncCollection handle."""
        return get_database_manager().get_collection(self._collection_name)

    @property
    def is_available(self) -> bool:
        """Returns True if the database is currently connected."""
        return get_database_manager().is_connected and self.collection is not None
