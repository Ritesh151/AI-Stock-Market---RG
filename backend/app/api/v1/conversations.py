"""
Conversations & Messages API Endpoints for RG AI.
Provides complete CRUD persistence for user chat sessions and messages in MongoDB.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.repositories.conversation_repository import ConversationRepository, get_conversation_repository
from app.repositories.message_repository import MessageRepository, get_message_repository
from app.schemas.common import ApiResponse
from app.schemas.persistence import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse,
)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=ApiResponse[List[ConversationResponse]])
async def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    user_id: str = Query("guest_user"),
    repo: ConversationRepository = Depends(get_conversation_repository),
) -> ApiResponse[List[ConversationResponse]]:
    """Lists conversations for the specified user."""
    items = await repo.list_conversations(user_id=user_id, limit=limit, skip=skip)
    return ApiResponse(success=True, data=items)


@router.post("", response_model=ApiResponse[ConversationResponse], status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    user_id: str = Query("guest_user"),
    repo: ConversationRepository = Depends(get_conversation_repository),
) -> ApiResponse[ConversationResponse]:
    """Creates a new conversation thread."""
    c = await repo.create_conversation(
        user_id=user_id,
        title=payload.title or "New Analysis",
    )
    return ApiResponse(
        success=True,
        data=ConversationResponse(
            conversation_id=c.conversation_id,
            user_id=c.user_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=c.message_count,
            status=c.status,
        ),
    )


@router.get("/{conversation_id}", response_model=ApiResponse[ConversationResponse])
async def get_conversation(
    conversation_id: str,
    user_id: str = Query("guest_user"),
    repo: ConversationRepository = Depends(get_conversation_repository),
) -> ApiResponse[ConversationResponse]:
    """Fetches details of a single conversation."""
    c = await repo.get_conversation(user_id=user_id, conversation_id=conversation_id)
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ApiResponse(
        success=True,
        data=ConversationResponse(
            conversation_id=c.conversation_id,
            user_id=c.user_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=c.message_count,
            status=c.status,
        ),
    )


@router.patch("/{conversation_id}", response_model=ApiResponse[ConversationResponse])
async def update_conversation(
    conversation_id: str,
    payload: ConversationUpdate,
    user_id: str = Query("guest_user"),
    repo: ConversationRepository = Depends(get_conversation_repository),
) -> ApiResponse[ConversationResponse]:
    """Updates the title of a conversation."""
    c = await repo.rename_conversation(user_id=user_id, conversation_id=conversation_id, new_title=payload.title)
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ApiResponse(
        success=True,
        data=ConversationResponse(
            conversation_id=c.conversation_id,
            user_id=c.user_id,
            title=c.title,
            created_at=c.created_at,
            updated_at=c.updated_at,
            message_count=c.message_count,
            status=c.status,
        ),
    )


@router.delete("/{conversation_id}", response_model=ApiResponse[dict])
async def delete_conversation(
    conversation_id: str,
    user_id: str = Query("guest_user"),
    conv_repo: ConversationRepository = Depends(get_conversation_repository),
    msg_repo: MessageRepository = Depends(get_message_repository),
) -> ApiResponse[dict]:
    """Deletes a conversation and its associated messages."""
    deleted = await conv_repo.delete_conversation(user_id=user_id, conversation_id=conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await msg_repo.delete_conversation_messages(user_id=user_id, conversation_id=conversation_id)
    return ApiResponse(success=True, data={"deleted": True, "conversation_id": conversation_id})


@router.get("/{conversation_id}/messages", response_model=ApiResponse[List[MessageResponse]])
async def list_messages(
    conversation_id: str,
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
    user_id: str = Query("guest_user"),
    conv_repo: ConversationRepository = Depends(get_conversation_repository),
    msg_repo: MessageRepository = Depends(get_message_repository),
) -> ApiResponse[List[MessageResponse]]:
    """Retrieves all messages for a conversation in chronological order."""
    c = await conv_repo.get_conversation(user_id=user_id, conversation_id=conversation_id)
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await msg_repo.get_messages(user_id=user_id, conversation_id=conversation_id, limit=limit, skip=skip)
    return ApiResponse(success=True, data=messages)


@router.post(
    "/{conversation_id}/messages",
    response_model=ApiResponse[MessageResponse],
    status_code=status.HTTP_201_CREATED,
)
async def append_message(
    conversation_id: str,
    payload: MessageCreate,
    user_id: str = Query("guest_user"),
    conv_repo: ConversationRepository = Depends(get_conversation_repository),
    msg_repo: MessageRepository = Depends(get_message_repository),
) -> ApiResponse[MessageResponse]:
    """Appends a message to a conversation thread and updates thread message count."""
    c = await conv_repo.get_conversation(user_id=user_id, conversation_id=conversation_id)
    if not c:
        # Create conversation automatically if it doesn't exist yet
        c = await conv_repo.create_conversation(
            user_id=user_id,
            title=payload.content[:40],
            conversation_id=conversation_id,
        )

    msg = await msg_repo.append_message(
        conversation_id=conversation_id,
        user_id=user_id,
        payload=payload,
    )

    return ApiResponse(
        success=True,
        data=MessageResponse(
            message_id=msg.message_id,
            conversation_id=msg.conversation_id,
            user_id=msg.user_id,
            role=msg.role,
            content=msg.content,
            request_id=msg.request_id,
            response_type=msg.response_type,
            validated_json=msg.validated_json,
            request_status=msg.request_status,
            created_at=msg.created_at,
        ),
    )
