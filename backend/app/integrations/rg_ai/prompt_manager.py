"""
RG AI Prompt Manager.
Validates, sanitizes, and structures prompts without mutating user intent.
"""

import re
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.integrations.rg_ai.gpt_config import (
    CURRENT_PROMPT_TEMPLATE_VERSION,
    MAX_METADATA_KEYS,
    MAX_PROMPT_LENGTH,
    MIN_PROMPT_LENGTH,
)
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger("integrations.rg_ai.prompt_manager")

# Suspicious path or protocol patterns to reject in user-submitted metadata
_DISALLOWED_PATTERNS = re.compile(
    r"(file://|chrome://|about:|javascript:|data:|/etc/|/var/|/usr/|/root/|C:\\|[a-zA-Z]:\\)",
    re.IGNORECASE,
)


class PreparedPrompt(BaseModel):
    """Immutable prepared prompt model ready for adapter execution."""

    original_prompt: str
    cleaned_prompt: str
    template_version: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[str] = None


class PromptManager:
    """Manages prompt validation, metadata sanitization, and packaging."""

    def __init__(self, template_version: str = CURRENT_PROMPT_TEMPLATE_VERSION) -> None:
        self.template_version = template_version

    def validate_and_prepare(
        self,
        raw_prompt: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PreparedPrompt:
        """
        Validates the prompt and metadata, ensuring safe structure and length bounds.
        Never mutates user intent or appends executable code.
        """
        if not isinstance(raw_prompt, str):
            raise AppException(
                message="Prompt must be a valid text string.",
                code="INVALID_PROMPT_TYPE",
                status_code=422,
            )

        trimmed = raw_prompt.strip()
        if not trimmed:
            raise AppException(
                message="Prompt cannot be empty or whitespace-only.",
                code="EMPTY_PROMPT",
                status_code=422,
            )

        if len(trimmed) < MIN_PROMPT_LENGTH:
            raise AppException(
                message=f"Prompt must be at least {MIN_PROMPT_LENGTH} characters.",
                code="PROMPT_TOO_SHORT",
                status_code=422,
            )

        if len(raw_prompt) > MAX_PROMPT_LENGTH:
            raise AppException(
                message=f"Prompt exceeds maximum allowable length of {MAX_PROMPT_LENGTH} characters.",
                code="PROMPT_TOO_LONG",
                status_code=422,
            )

        sanitized_metadata = self._sanitize_metadata(metadata)

        return PreparedPrompt(
            original_prompt=raw_prompt,
            cleaned_prompt=trimmed,
            template_version=self.template_version,
            metadata=sanitized_metadata,
            conversation_id=conversation_id.strip() if conversation_id else None,
        )

    def _sanitize_metadata(self, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sanitizes input metadata to prevent arbitrary path or URL injection.
        """
        if not metadata:
            return {}

        if not isinstance(metadata, dict):
            raise AppException(
                message="Metadata must be a key-value dictionary.",
                code="INVALID_METADATA_TYPE",
                status_code=422,
            )

        if len(metadata) > MAX_METADATA_KEYS:
            raise AppException(
                message=f"Metadata cannot exceed {MAX_METADATA_KEYS} keys.",
                code="METADATA_LIMIT_EXCEEDED",
                status_code=422,
            )

        clean: Dict[str, Any] = {}
        for key, value in metadata.items():
            if not isinstance(key, str) or len(key) > 50:
                continue

            str_val = str(value)
            if _DISALLOWED_PATTERNS.search(str_val):
                logger.warning(f"Rejected suspicious metadata key '{key}': contains restricted pattern")
                continue

            # Limit value size to 500 characters
            if len(str_val) > 500:
                continue

            clean[key] = value

        return clean


_prompt_manager_instance: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """Returns singleton instance of PromptManager."""
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance
