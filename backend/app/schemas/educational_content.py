"""
Educational Content Pydantic Schema.
Strict validation of Indian stock market educational resources and trading concepts.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class EducationalContentSchema(BaseModel):
    """Schema for structured trading curriculum and conceptual education."""

    topic: str = Field(..., description="Educational concept or topic title")
    category: str = Field(..., description="Subject category (e.g. Technical Analysis, Risk Management)")
    summary: str = Field(..., description="Core concept summary")
    key_concepts: List[str] = Field(default_factory=list, description="Key takeaways or bullet principles")
    practical_example: Optional[str] = Field(
        default=None, description="Illustrative scenario using Indian equities"
    )
    risk_management_tips: List[str] = Field(
        default_factory=list, description="Associated capital preservation and risk rules"
    )
    glossary_terms: Optional[Dict[str, str]] = Field(
        default=None, description="Definitions for relevant financial terms"
    )
