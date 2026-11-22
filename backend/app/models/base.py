"""
Base Mongo Document Model Architecture.
Prepares Pydantic v2 integration with MongoDB BSON ObjectId and timestamps.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field


class BaseMongoDocument(BaseModel):
    """
    Abstract base document model for MongoDB documents.
    Full database integration will be established in Phase 2.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when document was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when document was last modified",
    )

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
