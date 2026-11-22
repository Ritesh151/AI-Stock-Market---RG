"""
User Repository for MongoDB.
Manages user accounts, secure PBKDF2 password hashes, and unique email constraints.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, Optional
from app.core.logging import get_logger
from app.repositories.base import BaseRepository, sanitize_filter
from app.schemas.persistence import (
    UserCreate,
    UserModel,
    hash_password,
)

logger = get_logger("user_repo")


class UserRepository(BaseRepository[UserModel]):
    """Repository handling user entity persistence."""

    def __init__(self):
        super().__init__(collection_name="users")
        # In-memory fallback cache for disconnected mode
        self._fallback_users: Dict[str, UserModel] = {}

    async def get_by_id(self, user_id: str) -> Optional[UserModel]:
        """Fetch user by user_id."""
        if self.is_available and self.collection is not None:
            doc = await self.collection.find_one({"user_id": user_id})
            if doc:
                doc.pop("_id", None)
                return UserModel(**doc)
            return None
        return self._fallback_users.get(user_id)

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """Fetch user by unique email."""
        clean_email = email.lower().strip()
        if self.is_available and self.collection is not None:
            doc = await self.collection.find_one({"email": clean_email})
            if doc:
                doc.pop("_id", None)
                return UserModel(**doc)
            return None

        for user in self._fallback_users.values():
            if user.email.lower() == clean_email:
                return user
        return None

    async def create_user(self, payload: UserCreate) -> UserModel:
        """Create a new user with hashed password."""
        existing = await self.get_by_email(payload.email)
        if existing:
            raise ValueError(f"User with email '{payload.email}' already exists.")

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        pwd_hash = hash_password(payload.password) if payload.password else None

        user = UserModel(
            user_id=user_id,
            email=payload.email.lower().strip(),
            display_name=payload.display_name.strip(),
            password_hash=pwd_hash,
            role=payload.role,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        if self.is_available and self.collection is not None:
            user_dict = user.model_dump()
            await self.collection.insert_one(user_dict)
        else:
            self._fallback_users[user.user_id] = user

        return user

    async def update_last_login(self, user_id: str) -> None:
        """Update last login timestamp."""
        now = datetime.now(timezone.utc)
        if self.is_available and self.collection is not None:
            await self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"last_login_at": now, "updated_at": now}},
            )
        elif user_id in self._fallback_users:
            self._fallback_users[user_id].last_login_at = now


_user_repository: Optional[UserRepository] = None


def get_user_repository() -> UserRepository:
    """Singleton getter for UserRepository."""
    global _user_repository
    if _user_repository is None:
        _user_repository = UserRepository()
    return _user_repository
