"""
RG AI Conversation Manager.
Tracks active conversation threads and associations between requests and conversation sessions.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class ConversationSession(BaseModel):
    """Represents a conversation session thread."""

    conversation_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    request_ids: List[str] = Field(default_factory=list)
    title: Optional[str] = None


class ConversationManager:
    """In-memory conversation manager for tracking conversation threads."""

    def __init__(self) -> None:
        self._conversations: Dict[str, ConversationSession] = {}

    def get_or_create(self, conversation_id: Optional[str] = None, title: Optional[str] = None) -> ConversationSession:
        """Retrieves existing conversation or creates a new one."""
        cid = conversation_id.strip() if conversation_id and conversation_id.strip() else f"conv_{uuid.uuid4().hex[:12]}"
        if cid not in self._conversations:
            self._conversations[cid] = ConversationSession(conversation_id=cid, title=title)
        return self._conversations[cid]

    def link_request(self, conversation_id: str, request_id: str) -> None:
        """Associates a request ID with a conversation thread."""
        session = self.get_or_create(conversation_id)
        if request_id not in session.request_ids:
            session.request_ids.append(request_id)
        session.updated_at = datetime.now(timezone.utc)

    def get_requests(self, conversation_id: str) -> List[str]:
        """Returns request IDs associated with a conversation."""
        if conversation_id in self._conversations:
            return list(self._conversations[conversation_id].request_ids)
        return []

    def get_session(self, conversation_id: str) -> Optional[ConversationSession]:
        """Retrieves a conversation session."""
        return self._conversations.get(conversation_id)


_conversation_manager_instance: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """Returns singleton instance of ConversationManager."""
    global _conversation_manager_instance
    if _conversation_manager_instance is None:
        _conversation_manager_instance = ConversationManager()
    return _conversation_manager_instance
