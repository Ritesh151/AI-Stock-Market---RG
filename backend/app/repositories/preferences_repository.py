"""
User Preferences Repository for MongoDB.
Stores user interface, default exchange, chart configuration, and learning settings.
"""

from datetime import datetime, timezone
from typing import Dict, Optional
from pymongo import ReturnDocument

from app.core.logging import get_logger
from app.repositories.base import BaseRepository
from app.schemas.persistence import UserPreferencesModel, UserPreferencesUpdate

logger = get_logger("preferences_repo")


class PreferencesRepository(BaseRepository[UserPreferencesModel]):
    """Repository handling persistent user preferences."""

    def __init__(self):
        super().__init__(collection_name="user_preferences")
        self._fallback_store: Dict[str, UserPreferencesModel] = {}

    async def get_preferences(self, user_id: str = "guest_user") -> UserPreferencesModel:
        """Fetch user preferences, creating standard defaults if not present."""
        if self.is_available and self.collection is not None:
            doc = await self.collection.find_one({"user_id": user_id})
            if doc:
                doc.pop("_id", None)
                return UserPreferencesModel(**doc)

            # Insert defaults
            prefs = UserPreferencesModel(user_id=user_id)
            await self.collection.insert_one(prefs.model_dump())
            return prefs

        # In-memory fallback
        if user_id not in self._fallback_store:
            self._fallback_store[user_id] = UserPreferencesModel(user_id=user_id)
        return self._fallback_store[user_id]

    async def update_preferences(
        self, user_id: str, updates: UserPreferencesUpdate
    ) -> UserPreferencesModel:
        """Update selective preference fields."""
        update_data = {k: v for k, v in updates.model_dump(exclude_unset=True).items() if v is not None}
        now = datetime.now(timezone.utc)
        update_data["updated_at"] = now

        if self.is_available and self.collection is not None:
            doc = await self.collection.find_one_and_update(
                {"user_id": user_id},
                {"$set": update_data},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
            if doc:
                doc.pop("_id", None)
                return UserPreferencesModel(**doc)

        # In-memory fallback
        current = await self.get_preferences(user_id)
        updated_dict = current.model_dump()
        updated_dict.update(update_data)
        new_prefs = UserPreferencesModel(**updated_dict)
        self._fallback_store[user_id] = new_prefs
        return new_prefs


_preferences_repository: Optional[PreferencesRepository] = None


def get_preferences_repository() -> PreferencesRepository:
    """Singleton getter for PreferencesRepository."""
    global _preferences_repository
    if _preferences_repository is None:
        _preferences_repository = PreferencesRepository()
    return _preferences_repository
