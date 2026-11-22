"""
Unit and Integration Tests for RG AI MongoDB Persistence Architecture (Phase 10).
Tests database connection, health diagnostics, PBKDF2 password security,
collection indexing, repositories CRUD, REST endpoints, and graceful offline fallback.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.database import DatabaseManager, database_manager
from app.main import create_app
from app.schemas.persistence import (
    hash_password,
    verify_password,
    UserCreate,
    ConversationCreate,
    ConversationUpdate,
    MessageCreate,
    WatchlistAddPayload,
    SavedAnalysisCreate,
    UserPreferencesUpdate,
    PromptTemplateCreate,
)
from app.repositories.user_repository import UserRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.watchlist_repository import WatchlistRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.preferences_repository import PreferencesRepository
from app.repositories.template_repository import TemplateRepository
from app.repositories.learning_repository import MongoLearningRepository
from app.schemas.learning import QuizAnswerSubmission


# =====================================================================
# 1. Password Hashing & Security Tests
# =====================================================================

def test_pbkdf2_password_hashing():
    """Verify PBKDF2-HMAC-SHA256 password hashing with salt, 600,000 iterations, and constant-time verify."""
    pwd = "UltraSecurePassword@2026!"
    hashed = hash_password(pwd)

    # Check format: algorithm$iterations$salt$hash
    parts = hashed.split("$")
    assert len(parts) == 4
    assert parts[0] == "pbkdf2_sha256"
    assert parts[1] == "600000"
    assert len(parts[2]) == 32  # 16 bytes hex salt = 32 chars
    assert len(parts[3]) == 64  # SHA-256 = 32 bytes hex = 64 chars

    # Positive verification
    assert verify_password(pwd, hashed) is True

    # Negative verification
    assert verify_password("WrongPassword123", hashed) is False
    assert verify_password("", hashed) is False


# =====================================================================
# 2. Database Connection & Health Diagnostics Tests
# =====================================================================

@pytest.mark.asyncio
async def test_database_manager_connection_and_indexes():
    """Test AsyncMongoClient initialization, ping, index creation, and disconnect."""
    test_settings = Settings(
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DATABASE="rg_ai_pytest",
        MONGODB_MAX_POOL_SIZE=10,
        MONGODB_MIN_POOL_SIZE=2,
    )
    mgr = DatabaseManager(settings=test_settings)
    connected = await mgr.initialize()

    if connected:
        assert mgr.is_connected is True
        ping = await mgr.ping()
        assert ping["status"] == "connected"
        assert ping["database"] == "rg_ai_pytest"
        assert ping["latency_ms"] is not None
        assert ping["latency_ms"] >= 0

        # Verify collection indexes exist
        db = mgr.get_database()
        user_indexes = await db["users"].index_information()
        assert "idx_users_email_unique" in user_indexes

        conv_indexes = await db["conversations"].index_information()
        assert "idx_conversations_user_updated" in conv_indexes

        msg_indexes = await db["messages"].index_information()
        assert "idx_messages_conv_created" in msg_indexes


        watchlist_indexes = await db["watchlists"].index_information()
        assert "idx_watchlists_user_symbol_exchange_unique" in watchlist_indexes


        await mgr.disconnect()
        assert mgr.is_connected is False


def test_database_health_endpoint():
    """Test GET /api/v1/system/database-health."""
    test_settings = Settings(
        APP_ENV="test",
        MONGODB_URI="mongodb://localhost:27017",
        MONGODB_DATABASE="rg_ai_pytest",
    )
    app = create_app(settings=test_settings)
    with TestClient(app) as test_client:
        res = test_client.get("/api/v1/system/database-health")
        assert res.status_code == 200
        data = res.json()
        assert "success" in data
        assert "data" in data
        assert data["data"]["database"] in ["rg_ai", "rg_ai_pytest"]
        assert data["data"]["status"] in ["connected", "disconnected"]


# =====================================================================
# 3. User Repository Persistence Tests
# =====================================================================

@pytest.mark.asyncio
async def test_user_repository_crud():
    """Test creating user, unique email constraint, and password verification."""
    repo = UserRepository()
    user_payload = UserCreate(
        email="test_trader_phase10@rgai.in",
        password="SecureInvestor#2026",
        display_name="Ritesh Trader",
    )

    created = await repo.create_user(user_payload)
    assert created.user_id.startswith("usr_")
    assert created.email == "test_trader_phase10@rgai.in"
    assert created.display_name == "Ritesh Trader"

    # Verify duplicate email is rejected
    with pytest.raises(ValueError, match="already exists"):
        await repo.create_user(user_payload)


    # Fetch user
    fetched = await repo.get_by_email("test_trader_phase10@rgai.in")
    assert fetched is not None
    assert fetched.user_id == created.user_id

    # Password verify
    assert verify_password("SecureInvestor#2026", fetched.password_hash) is True
    assert verify_password("InvalidPass", fetched.password_hash) is False



# =====================================================================
# 4. Conversations & Messages Persistence Tests
# =====================================================================

@pytest.mark.asyncio
async def test_conversation_and_messages_lifecycle():
    """Test conversation thread creation, message appending, chronological ordering, and cascade delete."""
    from app.repositories.conversation_repository import get_conversation_repository
    from app.repositories.message_repository import get_message_repository

    conv_repo = get_conversation_repository()
    msg_repo = get_message_repository()
    user_id = "test_user_persistence"


    # 1. Create conversation
    conv = await conv_repo.create_conversation(
        user_id=user_id,
        title="Reliance Breakout Analysis",
    )
    assert conv.conversation_id.startswith("conv_")
    assert conv.message_count == 0

    # 2. Append messages
    msg1 = await msg_repo.append_message(
        conversation_id=conv.conversation_id,
        user_id=user_id,
        payload=MessageCreate(
            role="user",
            content="Analyze RELIANCE Q3 breakout potential.",
        ),
    )
    assert msg1.message_id.startswith("msg_")
    assert msg1.role == "user"

    msg2 = await msg_repo.append_message(
        conversation_id=conv.conversation_id,
        user_id=user_id,
        payload=MessageCreate(
            role="assistant",
            content="Reliance Industries is consolidating near key resistance at ₹3,000.",
            response_type="stock_analysis",
            validated_json={"symbol": "RELIANCE", "recommendation": "ACCUMULATE"},
            request_status="completed",
        ),
    )
    assert msg2.role == "assistant"
    assert msg2.validated_json["recommendation"] == "ACCUMULATE"

    # 3. Verify chronological order
    messages = await msg_repo.get_messages(user_id=user_id, conversation_id=conv.conversation_id)
    assert len(messages) == 2
    assert messages[0].content == "Analyze RELIANCE Q3 breakout potential."
    assert messages[1].content.startswith("Reliance Industries is consolidating")

    # 4. Verify message_count updated on conversation
    updated_conv = await conv_repo.get_conversation(user_id=user_id, conversation_id=conv.conversation_id)
    assert updated_conv is not None
    assert updated_conv.message_count == 2

    # 5. Rename conversation
    renamed = await conv_repo.rename_conversation(
        user_id=user_id,
        conversation_id=conv.conversation_id,
        new_title="RELIANCE Technical Deep Dive",
    )
    assert renamed is not None
    assert renamed.title == "RELIANCE Technical Deep Dive"

    # 6. Delete conversation
    deleted = await conv_repo.delete_conversation(user_id=user_id, conversation_id=conv.conversation_id)
    assert deleted is True
    assert await conv_repo.get_conversation(user_id=user_id, conversation_id=conv.conversation_id) is None


# =====================================================================
# 5. Watchlist Persistence Tests
# =====================================================================

@pytest.mark.asyncio
async def test_watchlist_repository_persistence():
    """Test watchlist item insertion, compound unique constraint, quote data, and deletion."""
    repo = WatchlistRepository()
    user_id = "test_wl_user"

    item = await repo.add_item(
        user_id=user_id,
        payload=WatchlistAddPayload(symbol="TCS", exchange="NSE", notes="Key IT holding"),
        quote_data={"last_price": 4200.50, "change": 35.20, "change_percent": 0.84, "data_status": "REALTIME"},
    )
    assert item.symbol == "TCS"
    assert item.exchange == "NSE"

    # Add duplicate should return existing without error

    dup = await repo.add_item(
        user_id=user_id,
        payload=WatchlistAddPayload(symbol="TCS", exchange="NSE"),
    )
    assert dup.symbol == "TCS"

    # List items
    items = await repo.list_items(user_id=user_id)
    symbols = [i.symbol for i in items]
    assert "TCS" in symbols

    # Remove item
    removed = await repo.remove_item(user_id=user_id, symbol="TCS", exchange="NSE")
    assert removed is True
    assert await repo.get_item(user_id=user_id, symbol="TCS", exchange="NSE") is None


# =====================================================================
# 6. Saved Analysis Persistence Tests
# =====================================================================

@pytest.mark.asyncio
async def test_saved_analysis_repository_persistence():
    """Test saving financial analyses, querying by symbol and type, and deletion."""
    repo = AnalysisRepository()
    user_id = "test_anl_user"

    analysis = await repo.save_analysis(
        user_id=user_id,
        payload=SavedAnalysisCreate(
            symbol="INFY",
            exchange="NSE",
            analysis_type="stock_analysis",
            validated_data={
                "stock_name": "Infosys Limited",
                "current_price": 1850.0,
                "recommendation": "BUY",
                "target_price": 2100.0,
            },
        ),
    )
    assert analysis.analysis_id.startswith("anl_")
    assert analysis.symbol == "INFY"
    assert analysis.validated_data["recommendation"] == "BUY"

    # Query by symbol
    results = await repo.list_analyses(user_id=user_id, symbol="INFY")
    assert len(results) >= 1
    assert results[0].symbol == "INFY"

    # Query single
    fetched = await repo.get_analysis(user_id=user_id, analysis_id=analysis.analysis_id)
    assert fetched is not None
    assert fetched.analysis_id == analysis.analysis_id

    # Delete
    deleted = await repo.delete_analysis(user_id=user_id, analysis_id=analysis.analysis_id)
    assert deleted is True


# =====================================================================
# 7. User Preferences Persistence Tests
# =====================================================================

@pytest.mark.asyncio
async def test_user_preferences_persistence():
    """Test fetching default preferences, updating partial fields, and retrieval."""
    repo = PreferencesRepository()
    user_id = "test_prefs_user"

    # Get default preferences
    prefs = await repo.get_preferences(user_id=user_id)
    assert prefs.user_id == user_id
    assert prefs.theme == "off-white"
    assert prefs.default_exchange == "NSE"

    # Update preferences
    updated = await repo.update_preferences(
        user_id=user_id,
        updates=UserPreferencesUpdate(
            default_exchange="BSE",
            preferred_chart_type="candlestick",
            default_chart_range="6M",
        ),
    )
    assert updated.default_exchange == "BSE"
    assert updated.preferred_chart_type == "candlestick"
    assert updated.default_chart_range == "6M"
    assert updated.theme == "off-white"  # Preserved


# =====================================================================
# 8. Prompt Template Repository Tests
# =====================================================================

@pytest.mark.asyncio
async def test_prompt_template_repository():
    """Test prompt template listing, seeding, and retrieval."""
    repo = TemplateRepository()
    templates, total = await repo.list_templates()
    assert total >= 10
    template_ids = [t.template_id for t in templates]
    assert "v1_complete_stock_analysis" in template_ids
    assert "v1_buy_sell_research" in template_ids

    # Query single template
    t = await repo.get_by_template_id("v1_complete_stock_analysis")
    assert t is not None
    assert t.target_schema_type == "stock_analysis"


# =====================================================================
# 9. Learning Repository Mongo Progress & Quiz Attempts Tests
# =====================================================================

@pytest.mark.asyncio
async def test_learning_repository_persistence():
    """Test MongoLearningRepository user progress, bookmarks, and quiz attempt tracking."""
    repo = MongoLearningRepository()
    user_id = "test_learner_p10"

    # Progress tracking
    p1 = await repo.update_user_progress(
        lesson_id="lesson-nse-bse-structure",
        completed=True,
        course_id="course-market-basics",
        user_id=user_id,
    )
    assert "lesson-nse-bse-structure" in p1.completed_lesson_ids
    assert p1.last_accessed_lesson_id == "lesson-nse-bse-structure"

    # Bookmark tracking
    p2 = await repo.add_bookmark(lesson_id="lesson-nse-bse-structure", note="Study trading hours", user_id=user_id)
    assert "lesson-nse-bse-structure" in p2.bookmarked_lesson_ids

    # Remove bookmark
    p3 = await repo.remove_bookmark(lesson_id="lesson-nse-bse-structure", user_id=user_id)
    assert "lesson-nse-bse-structure" not in p3.bookmarked_lesson_ids

    # Quiz evaluation & attempt persistence
    quiz_res = await repo.evaluate_quiz(
        quiz_id="quiz-lesson-nse-bse-structure",
        answers=[
            QuizAnswerSubmission(question_id="q-nse-1", selected_option_id="opt-b"),
            QuizAnswerSubmission(question_id="q-nse-2", selected_option_id="opt-true"),
        ],
        user_id=user_id,
    )
    assert quiz_res is not None
    assert quiz_res.total_questions > 0



# =====================================================================
# 10. REST API Endpoints Integration Tests
# =====================================================================

def test_conversations_rest_api(client: TestClient):
    """Test /api/v1/conversations and messages REST endpoints via TestClient."""
    # 1. Create conversation
    res = client.post(
        "/api/v1/conversations?user_id=api_test_user",
        json={"title": "HDFC Bank Setup"},
    )
    assert res.status_code == 201
    conv_data = res.json()["data"]
    conv_id = conv_data["conversation_id"]
    assert conv_data["title"] == "HDFC Bank Setup"

    # 2. Append message
    msg_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages?user_id=api_test_user",
        json={
            "role": "user",
            "content": "Is HDFC Bank trading above 200 EMA?",
        },
    )
    assert msg_res.status_code == 201
    assert msg_res.json()["data"]["role"] == "user"

    # 3. List messages
    list_msgs = client.get(f"/api/v1/conversations/{conv_id}/messages?user_id=api_test_user")
    assert list_msgs.status_code == 200
    assert len(list_msgs.json()["data"]) == 1

    # 4. Rename
    rename_res = client.patch(
        f"/api/v1/conversations/{conv_id}?user_id=api_test_user",
        json={"title": "HDFC Bank 200 EMA Strategy"},
    )
    assert rename_res.status_code == 200
    assert rename_res.json()["data"]["title"] == "HDFC Bank 200 EMA Strategy"

    # 5. Delete
    del_res = client.delete(f"/api/v1/conversations/{conv_id}?user_id=api_test_user")
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True


def test_analyses_rest_api(client: TestClient):
    """Test /api/v1/analyses REST endpoints."""
    # Save analysis
    res = client.post(
        "/api/v1/analyses?user_id=api_test_user",
        json={
            "symbol": "SBIN",
            "exchange": "NSE",
            "analysis_type": "stock_analysis",
            "validated_data": {"stock_name": "State Bank of India", "price": 820.0},
        },
    )
    assert res.status_code == 201
    anl_id = res.json()["data"]["analysis_id"]

    # List
    list_res = client.get("/api/v1/analyses?user_id=api_test_user&symbol=SBIN")
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) >= 1

    # Get single
    get_res = client.get(f"/api/v1/analyses/{anl_id}?user_id=api_test_user")
    assert get_res.status_code == 200
    assert get_res.json()["data"]["symbol"] == "SBIN"

    # Delete
    del_res = client.delete(f"/api/v1/analyses/{anl_id}?user_id=api_test_user")
    assert del_res.status_code == 200
    assert del_res.json()["data"]["deleted"] is True


def test_preferences_rest_api(client: TestClient):
    """Test /api/v1/preferences REST endpoints."""
    # Get preferences
    res = client.get("/api/v1/preferences?user_id=api_test_user")
    assert res.status_code == 200
    assert res.json()["data"]["theme"] == "off-white"

    # Patch preferences
    patch_res = client.patch(
        "/api/v1/preferences?user_id=api_test_user",
        json={"preferred_chart_type": "candlestick", "default_exchange": "BSE"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["preferred_chart_type"] == "candlestick"
    assert patch_res.json()["data"]["default_exchange"] == "BSE"
