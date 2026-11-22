"""
MongoDB Async Database Manager for RG AI.
Provides managed asynchronous connection pooling, lifecycle management,
connection health probing, and idempotent index initialization using PyMongo Async API.
"""

import time
from typing import Any, Dict, Optional
from pymongo import ASCENDING, DESCENDING, AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import ConnectionFailure, PyMongoError

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("database")


class DatabaseManager:
    """
    Centralized singleton managing asynchronous MongoDB client lifecycle,
    connection pooling, health checks, and collections.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()
        self._client: Optional[AsyncMongoClient] = None
        self._database: Optional[AsyncDatabase] = None
        self._is_connected: bool = False
        self._last_ping_ms: float = 0.0

    @property
    def is_connected(self) -> bool:
        """Returns True if the client is connected and active."""
        return self._is_connected and self._client is not None

    @property
    def client(self) -> Optional[AsyncMongoClient]:
        """Returns the active AsyncMongoClient instance."""
        return self._client

    @property
    def database(self) -> Optional[AsyncDatabase]:
        """Returns the active AsyncDatabase instance."""
        return self._database

    def get_database(self) -> Optional[AsyncDatabase]:
        """Returns the active AsyncDatabase instance (callable style)."""
        return self._database


    def get_collection(self, name: str) -> Optional[AsyncCollection]:
        """Returns collection handle if database is active."""
        if self._database is None:
            return None
        return self._database[name]

    async def connect(self) -> bool:
        """
        Initializes MongoDB connection pool and creates indexes.
        Handles outages gracefully without crashing startup.
        """
        if self._client is not None:
            return self._is_connected

        uri = self._settings.MONGODB_URI

        db_name = self._settings.MONGODB_DATABASE

        if not uri or not uri.strip():
            logger.info("MONGODB_URI is not set; running in disconnected database mode.")
            self._is_connected = False
            return False

        try:
            logger.info(
                f"Initializing Async MongoDB connection pool (min={self._settings.MONGODB_MIN_POOL_SIZE}, max={self._settings.MONGODB_MAX_POOL_SIZE})..."
            )
            self._client = AsyncMongoClient(
                uri,
                maxPoolSize=self._settings.MONGODB_MAX_POOL_SIZE,
                minPoolSize=self._settings.MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=self._settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                connectTimeoutMS=self._settings.MONGODB_CONNECT_TIMEOUT_MS,
                retryWrites=True,
            )
            self._database = self._client[db_name]

            # Verify connection with quick ping
            start_time = time.perf_counter()
            await self._client.admin.command("ping")
            self._last_ping_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self._is_connected = True

            logger.info(
                f"Successfully connected to MongoDB database '{db_name}' in {self._last_ping_ms}ms."
            )

            # Initialize idempotent indexes
            await self._create_indexes()
            return True

        except (ConnectionFailure, PyMongoError) as exc:
            self._is_connected = False
            logger.warning(
                f"MongoDB connection could not be established ({exc}). "
                "Running in disconnected mode with graceful fallback."
            )
            return False
        except Exception as exc:
            self._is_connected = False
            logger.error(f"Unexpected error initializing MongoDB connection: {exc}")
            return False

    # Alias for lifecycle initialization
    initialize = connect

    async def _create_indexes(self) -> None:

        """
        Idempotently creates optimal indexes across all 12 core collections.
        """
        if self._database is None or not self._is_connected:
            return

        try:
            db = self._database

            # 1. users: unique email
            await db["users"].create_index(
                [("email", ASCENDING)], unique=True, name="idx_users_email_unique"
            )

            # 2. conversations: (user_id, updated_at), (user_id, conversation_id)
            await db["conversations"].create_index(
                [("user_id", ASCENDING), ("updated_at", DESCENDING)],
                name="idx_conversations_user_updated",
            )
            await db["conversations"].create_index(
                [("user_id", ASCENDING), ("conversation_id", ASCENDING)],
                unique=True,
                name="idx_conversations_user_conv_unique",
            )

            # 3. messages: (conversation_id, created_at), (user_id, created_at), unique message_id
            await db["messages"].create_index(
                [("conversation_id", ASCENDING), ("created_at", ASCENDING)],
                name="idx_messages_conv_created",
            )
            await db["messages"].create_index(
                [("user_id", ASCENDING), ("created_at", DESCENDING)],
                name="idx_messages_user_created",
            )
            await db["messages"].create_index(
                [("message_id", ASCENDING)],
                unique=True,
                name="idx_messages_id_unique",
            )

            # 4. watchlists: compound unique (user_id, symbol, exchange)
            await db["watchlists"].create_index(
                [("user_id", ASCENDING), ("symbol", ASCENDING), ("exchange", ASCENDING)],
                unique=True,
                name="idx_watchlists_user_symbol_exchange_unique",
            )

            # 5. saved_analyses: (user_id, symbol, created_at)
            await db["saved_analyses"].create_index(
                [("user_id", ASCENDING), ("symbol", ASCENDING), ("created_at", DESCENDING)],
                name="idx_analyses_user_symbol_created",
            )

            # 6. prompt_templates: unique template_id
            await db["prompt_templates"].create_index(
                [("template_id", ASCENDING)],
                unique=True,
                name="idx_templates_id_unique",
            )

            # 7. user_preferences: unique user_id
            await db["user_preferences"].create_index(
                [("user_id", ASCENDING)],
                unique=True,
                name="idx_preferences_user_unique",
            )

            # 8. learning_courses: unique id
            await db["learning_courses"].create_index(
                [("id", ASCENDING)],
                unique=True,
                name="idx_learning_courses_id_unique",
            )

            # 9. learning_progress: compound unique (user_id, course_id)
            await db["learning_progress"].create_index(
                [("user_id", ASCENDING), ("course_id", ASCENDING)],
                unique=True,
                name="idx_learning_progress_user_course_unique",
            )

            # 10. learning_bookmarks: compound unique (user_id, lesson_id)
            await db["learning_bookmarks"].create_index(
                [("user_id", ASCENDING), ("lesson_id", ASCENDING)],
                unique=True,
                name="idx_learning_bookmarks_user_lesson_unique",
            )

            # 11. quiz_attempts: (user_id, quiz_id, created_at)
            await db["quiz_attempts"].create_index(
                [("user_id", ASCENDING), ("quiz_id", ASCENDING), ("created_at", DESCENDING)],
                name="idx_quiz_attempts_user_quiz_created",
            )

            # 12. audit_logs: (user_id, timestamp)
            await db["audit_logs"].create_index(
                [("user_id", ASCENDING), ("timestamp", DESCENDING)],
                name="idx_audit_logs_user_timestamp",
            )

            logger.info("MongoDB indexes verified successfully across all collections.")

        except Exception as exc:
            logger.warning(f"Non-fatal error creating MongoDB indexes: {exc}")

    async def ping(self) -> Dict[str, Any]:
        """
        Executes a ping command to evaluate database latency and health.
        """
        if self._client is None or not self._is_connected:
            return {
                "status": "disconnected",
                "database": self._settings.MONGODB_DATABASE,
                "latency_ms": None,
                "message": "Database client is not connected.",
            }

        try:
            start_time = time.perf_counter()
            await self._client.admin.command("ping")
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            self._last_ping_ms = latency_ms
            return {
                "status": "connected",
                "database": self._settings.MONGODB_DATABASE,
                "latency_ms": latency_ms,
                "message": "MongoDB ping successful.",
            }
        except Exception as exc:
            self._is_connected = False
            return {
                "status": "disconnected",
                "database": self._settings.MONGODB_DATABASE,
                "latency_ms": None,
                "message": f"MongoDB ping failed: {str(exc)}",
            }

    async def disconnect(self) -> None:
        """
        Gracefully terminates database connection and releases pool sockets.
        """
        if self._client is not None:
            logger.info("Closing Async MongoDB connection pool...")
            try:
                await self._client.close()
            except Exception as exc:
                logger.debug(f"Notice closing MongoDB client: {exc}")
            finally:
                self._client = None
                self._database = None
                self._is_connected = False
                logger.info("Async MongoDB connection pool closed.")


# Singleton helper
_database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Returns singleton DatabaseManager instance."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager


# Global convenience singleton instance
database_manager: DatabaseManager = get_database_manager()

