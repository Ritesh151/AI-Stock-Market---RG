"""
Conversation Repository for MongoDB.
Manages persistent conversation threads, ownership boundaries, message counts, and ordering.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional
from pymongo import DESCENDING

from app.core.logging import get_logger
from app.repositories.base import BaseRepository, sanitize_filter
from app.schemas.persistence import ConversationModel, ConversationResponse

logger = get_logger("conv_repo")


class ConversationRepository(BaseRepository[ConversationModel]):
    """Repository handling conversation thread persistence."""

    def __init__(self):
        super().__init__(collection_name="conversations")
        self._fallback_store: Dict[str, ConversationModel] = {}

    async def create_conversation(
        self,
        user_id: str = "guest_user",
        title: str = "New Analysis",
        conversation_id: Optional[str] = None,
    ) -> ConversationModel:
        """Create a new conversation thread."""
        conv_id = conversation_id or f"conv_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        conv = ConversationModel(
            conversation_id=conv_id,
            user_id=user_id,
            title=title.strip() if title else "New Analysis",
            created_at=now,
            updated_at=now,
            message_count=0,
            status="active",
        )

        if self.is_available and self.collection is not None:
            await self.collection.insert_one(conv.model_dump())
        else:
            self._fallback_store[conv_id] = conv

        return conv

    async def get_conversation(
        self, user_id: str, conversation_id: str
    ) -> Optional[ConversationModel]:
        """Fetch a conversation strictly enforcing user ownership."""
        if self.is_available and self.collection is not None:
            doc = await self.collection.find_one(
                {"user_id": user_id, "conversation_id": conversation_id, "status": "active"}
            )
            if doc:
                doc.pop("_id", None)
                return ConversationModel(**doc)
            return None

        conv = self._fallback_store.get(conversation_id)
        if conv and conv.user_id == user_id and conv.status == "active":
            return conv
        return None

    async def list_conversations(
        self, user_id: str = "guest_user", limit: int = 50, skip: int = 0
    ) -> List[ConversationResponse]:
        """List active conversations ordered by updated_at descending."""
        if self.is_available and self.collection is not None:
            cursor = (
                self.collection.find(
                    {"user_id": user_id, "status": "active"}
                )
                .sort("updated_at", DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            results = []
            async for doc in cursor:
                doc.pop("_id", None)
                results.append(ConversationResponse(**doc))
            return results

        # Fallback in-memory
        user_convs = [
            c for c in self._fallback_store.values()
            if c.user_id == user_id and c.status == "active"
        ]
        user_convs.sort(key=lambda x: x.updated_at, reverse=True)
        return [
            ConversationResponse(
                conversation_id=c.conversation_id,
                user_id=c.user_id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=c.message_count,
                status=c.status,
            )
            for c in user_convs[skip : skip + limit]
        ]

    async def rename_conversation(
        self, user_id: str, conversation_id: str, new_title: str
    ) -> Optional[ConversationModel]:
        """Rename a conversation thread."""
        now = datetime.now(timezone.utc)
        clean_title = new_title.strip()

        if self.is_available and self.collection is not None:
            res = await self.collection.find_one_and_update(
                {"user_id": user_id, "conversation_id": conversation_id, "status": "active"},
                {"$set": {"title": clean_title, "updated_at": now}},
                return_document=True,
            )
            if res:
                res.pop("_id", None)
                return ConversationModel(**res)
            return None

        conv = self._fallback_store.get(conversation_id)
        if conv and conv.user_id == user_id and conv.status == "active":
            conv.title = clean_title
            conv.updated_at = now
            return conv
        return None

    async def delete_conversation(
        self, user_id: str, conversation_id: str
    ) -> bool:
        """Soft delete conversation thread."""
        now = datetime.now(timezone.utc)
        if self.is_available and self.collection is not None:
            res = await self.collection.update_one(
                {"user_id": user_id, "conversation_id": conversation_id},
                {"$set": {"status": "deleted", "updated_at": now}},
            )
            return res.modified_count > 0

        conv = self._fallback_store.get(conversation_id)
        if conv and conv.user_id == user_id:
            conv.status = "deleted"
            conv.updated_at = now
            return True
        return False

    async def increment_message_count(
        self, user_id: str, conversation_id: str
    ) -> None:
        """Increment message count and touch updated_at."""
        now = datetime.now(timezone.utc)
        if self.is_available and self.collection is not None:
            await self.collection.update_one(
                {"user_id": user_id, "conversation_id": conversation_id},
                {"$inc": {"message_count": 1}, "$set": {"updated_at": now}},
            )
        elif conversation_id in self._fallback_store:
            conv = self._fallback_store[conversation_id]
            conv.message_count += 1
            conv.updated_at = now


_conversation_repository: Optional[ConversationRepository] = None


def get_conversation_repository() -> ConversationRepository:
    """Singleton getter for ConversationRepository."""
    global _conversation_repository
    if _conversation_repository is None:
        _conversation_repository = ConversationRepository()
    return _conversation_repository
