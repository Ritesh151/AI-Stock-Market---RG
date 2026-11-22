"""
Pydantic Persistence Schemas & Domain Models for MongoDB.
Defines entity representations, creation payloads, sanitization rules, and secure user handling.
"""

from datetime import datetime, timezone
import hashlib
import os
import secrets
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# =====================================================================
# Secure Password Utilities
# =====================================================================

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with 600,000 iterations and a random salt.
    Format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
    """
    salt = secrets.token_bytes(16)
    iterations = 600_000
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${hash_bytes.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the stored PBKDF2 hash using constant-time comparison.
    """
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode("utf-8"), salt, iterations
        )
        return secrets.compare_digest(expected_hash, calculated_hash)
    except Exception:
        return False


# =====================================================================
# User Schemas
# =====================================================================

EMAIL_REGEX = r"^[\w\.\+\-]+@[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,}$"


class UserModel(BaseModel):
    """Internal user document in MongoDB users collection."""
    user_id: str
    email: str = Field(..., pattern=EMAIL_REGEX)
    display_name: str
    password_hash: Optional[str] = None
    role: Literal["user", "admin", "analyst"] = "user"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: Optional[datetime] = None


class UserCreate(BaseModel):
    """Payload to create a new user account."""
    email: str = Field(..., pattern=EMAIL_REGEX)
    display_name: str = Field(..., min_length=2, max_length=50)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    role: Literal["user", "admin", "analyst"] = "user"



class UserResponse(BaseModel):
    """Sanitized user public representation (never exposes password hash)."""
    user_id: str
    email: EmailStr
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


# =====================================================================
# Conversation & Message Schemas
# =====================================================================

class ConversationModel(BaseModel):
    """Conversation thread document stored in MongoDB conversations collection."""
    conversation_id: str
    user_id: str
    title: str = "New Analysis"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message_count: int = 0
    status: Literal["active", "archived", "deleted"] = "active"


class ConversationCreate(BaseModel):
    """Payload to create a conversation."""
    title: Optional[str] = Field("New Analysis", max_length=100)


class ConversationUpdate(BaseModel):
    """Payload to rename conversation."""
    title: str = Field(..., min_length=1, max_length=100)


class ConversationResponse(BaseModel):
    """Conversation summary returned to API clients."""
    conversation_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    status: str


class MessageModel(BaseModel):
    """Chat message stored in MongoDB messages collection."""
    message_id: str
    conversation_id: str
    user_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    request_id: Optional[str] = None
    response_type: Optional[str] = None
    validated_json: Optional[Dict[str, Any]] = None
    request_status: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageCreate(BaseModel):
    """Payload to append a message to a conversation."""
    message_id: Optional[str] = None
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)
    request_id: Optional[str] = None
    response_type: Optional[str] = None
    validated_json: Optional[Dict[str, Any]] = None
    request_status: Optional[str] = None


class MessageResponse(BaseModel):
    """Message representation returned to API clients."""
    message_id: str
    conversation_id: str
    user_id: str
    role: str
    content: str
    request_id: Optional[str] = None
    response_type: Optional[str] = None
    validated_json: Optional[Dict[str, Any]] = None
    request_status: Optional[str] = None
    created_at: datetime


# =====================================================================
# Watchlist Schemas
# =====================================================================

class WatchlistMongoItem(BaseModel):
    """Watchlist record in MongoDB watchlists collection."""
    user_id: str
    symbol: str
    exchange: str = "NSE"
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: Optional[str] = None


class WatchlistAddPayload(BaseModel):
    """Payload to add stock to watchlist."""
    symbol: str = Field(..., min_length=1, max_length=20)
    exchange: str = Field(default="NSE", pattern=r"^(NSE|BSE)$")
    notes: Optional[str] = Field(default=None, max_length=250)


# =====================================================================
# Saved Analysis Schemas
# =====================================================================

class SavedAnalysisModel(BaseModel):
    """Validated analysis saved by user in MongoDB saved_analyses collection."""
    analysis_id: str
    user_id: str
    conversation_id: Optional[str] = None
    symbol: str
    exchange: str = "NSE"
    analysis_type: str = "stock_analysis"
    validated_data: Dict[str, Any]
    schema_version: str = "1.0"
    data_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data_source: str = "RG AI Intelligence Engine"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SavedAnalysisCreate(BaseModel):
    """Payload to save an analysis."""
    conversation_id: Optional[str] = None
    symbol: str = Field(..., min_length=1, max_length=20)
    exchange: str = Field(default="NSE", pattern=r"^(NSE|BSE)$")
    analysis_type: str = Field(default="stock_analysis")
    validated_data: Dict[str, Any]
    schema_version: str = "1.0"
    data_source: Optional[str] = "RG AI Intelligence Engine"


# =====================================================================
# User Preferences Schemas
# =====================================================================

class UserPreferencesModel(BaseModel):
    """User preferences stored in MongoDB user_preferences collection."""
    user_id: str
    theme: Literal["off-white"] = "off-white"
    default_exchange: Literal["NSE", "BSE"] = "NSE"
    preferred_chart_type: Literal["area", "line", "candlestick"] = "area"
    default_chart_range: Literal["1D", "5D", "1M", "3M", "6M", "1Y", "5Y"] = "1M"
    dashboard_preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "show_news": True,
        "show_movers": True,
        "show_sentiment": True,
    })
    notification_preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "email_alerts": False,
        "market_open_alerts": True,
    })
    learning_preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "auto_advance_lesson": True,
        "show_hints": True,
    })
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserPreferencesUpdate(BaseModel):
    """Payload to update user preferences."""
    default_exchange: Optional[Literal["NSE", "BSE"]] = None
    preferred_chart_type: Optional[Literal["area", "line", "candlestick"]] = None
    default_chart_range: Optional[Literal["1D", "5D", "1M", "3M", "6M", "1Y", "5Y"]] = None
    dashboard_preferences: Optional[Dict[str, Any]] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    learning_preferences: Optional[Dict[str, Any]] = None


# =====================================================================
# Prompt Template Schemas
# =====================================================================

class PromptTemplateModel(BaseModel):
    """Versioned prompt template stored in MongoDB prompt_templates collection."""
    template_id: str
    name: str
    category: str = "financial_analysis"
    version: str = "1.0"
    prompt: str = ""
    target_schema_type: Optional[str] = "stock_analysis"
    instructions: Optional[str] = ""
    schema_version: str = "1.0"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PromptTemplateCreate(BaseModel):
    """Payload to create a prompt template."""
    template_id: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    category: str = "financial_analysis"
    prompt: Optional[str] = ""
    target_schema_type: Optional[str] = "stock_analysis"
    instructions: Optional[str] = ""
    version: str = "1.0"
    schema_version: str = "1.0"

    is_active: bool = True


# =====================================================================
# Database Health Schema
# =====================================================================

class DatabaseHealthResponse(BaseModel):
    """Sanitized database health response without sensitive credentials."""
    status: Literal["connected", "disconnected"]
    database: str
    latency_ms: Optional[float] = None
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
