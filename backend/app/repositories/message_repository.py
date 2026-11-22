"""
Message Repository for MongoDB.
Manages persistent chat messages, request telemetry, validated JSON schemas, and chronological ordering.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional
from pymongo import ASCENDING

from app.core.logging import get_logger
from app.repositories.base import BaseRepository
from app.repositories.conversation_repository import get_conversation_repository
from app.schemas.persistence import MessageCreate, MessageModel, MessageResponse

logger = get_logger("message_repo")


class MessageRepository(BaseRepository[MessageModel]):
    """Repository handling individual message persistence."""

    def __init__(self):
        super().__init__(collection_name="messages")
        self._fallback_store: Dict[str, List[MessageModel]] = {}

    async def append_message(
        self,
        conversation_id: str,
        user_id: str,
        payload: MessageCreate,
    ) -> MessageModel:
        """Appends a new message or updates existing message if message_id exists."""
        msg_id = payload.message_id or f"msg_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        msg = MessageModel(
            message_id=msg_id,
            conversation_id=conversation_id,
            user_id=user_id,
            role=payload.role,
            content=payload.content,
            request_id=payload.request_id,
            response_type=payload.response_type,
            validated_json=payload.validated_json,
            request_status=payload.request_status,
            created_at=now,
            updated_at=now,
        )

        if self.is_available and self.collection is not None:
            existing = await self.collection.find_one(
                {"conversation_id": conversation_id, "user_id": user_id, "message_id": msg_id}
            )
            if existing:
                await self.collection.update_one(
                    {"_id": existing["_id"]},
                    {
                        "$set": {
                            "content": payload.content,
                            "request_id": payload.request_id,
                            "response_type": payload.response_type,
                            "validated_json": payload.validated_json,
                            "request_status": payload.request_status,
                            "updated_at": now,
                        }
                    },
                )
                msg.created_at = existing.get("created_at", now)
                return msg
            else:
                await self.collection.insert_one(msg.model_dump())
        else:
            if conversation_id not in self._fallback_store:
                self._fallback_store[conversation_id] = []

            for idx, existing_m in enumerate(self._fallback_store[conversation_id]):
                if existing_m.message_id == msg_id and existing_m.user_id == user_id:
                    msg.created_at = existing_m.created_at
                    self._fallback_store[conversation_id][idx] = msg
                    return msg

            self._fallback_store[conversation_id].append(msg)

        # Update conversation message count and timestamp
        await get_conversation_repository().increment_message_count(user_id, conversation_id)
        return msg

    async def get_messages(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 100,
        skip: int = 0,
    ) -> List[MessageResponse]:
        """Fetch messages in strict chronological order with ID deduplication."""
        if self.is_available and self.collection is not None:
            cursor = (
                self.collection.find(
                    {"conversation_id": conversation_id, "user_id": user_id}
                )
                .sort("created_at", ASCENDING)
                .skip(skip)
                .limit(limit)
            )
            messages: List[MessageResponse] = []
            seen_ids = set()
            async for doc in cursor:
                doc.pop("_id", None)
                m_id = doc.get("message_id")
                if m_id and m_id in seen_ids:
                    continue
                if m_id:
                    seen_ids.add(m_id)
                messages.append(MessageResponse(**doc))
            return messages

        # Fallback store
        msgs = self._fallback_store.get(conversation_id, [])
        user_msgs = [m for m in msgs if m.user_id == user_id]
        user_msgs.sort(key=lambda m: m.created_at)

        seen_ids = set()
        deduped_msgs = []
        for m in user_msgs:
            if m.message_id not in seen_ids:
                seen_ids.add(m.message_id)
                deduped_msgs.append(m)

        return [
            MessageResponse(
                message_id=m.message_id,
                conversation_id=m.conversation_id,
                user_id=m.user_id,
                role=m.role,
                content=m.content,
                request_id=m.request_id,
                response_type=m.response_type,
                validated_json=m.validated_json,
                request_status=m.request_status,
                created_at=m.created_at,
            )
            for m in deduped_msgs[skip : skip + limit]
        ]

    async def delete_conversation_messages(
        self, user_id: str, conversation_id: str
    ) -> int:
        """Delete all messages for a specific conversation."""
        if self.is_available and self.collection is not None:
            res = await self.collection.delete_many(
                {"conversation_id": conversation_id, "user_id": user_id}
            )
            return res.deleted_count

        if conversation_id in self._fallback_store:
            original_len = len(self._fallback_store[conversation_id])
            self._fallback_store[conversation_id] = [
                m for m in self._fallback_store[conversation_id] if m.user_id != user_id
            ]
            return original_len - len(self._fallback_store[conversation_id])
        return 0


_message_repository: Optional[MessageRepository] = None


def get_message_repository() -> MessageRepository:
    """Singleton getter for MessageRepository."""
    global _message_repository
    if _message_repository is None:
        _message_repository = MessageRepository()
    return _message_repository
