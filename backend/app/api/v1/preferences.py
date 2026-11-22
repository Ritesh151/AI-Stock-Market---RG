"""
User Preferences API Endpoints for RG AI.
Provides persistent user preference management in MongoDB.
"""

from fastapi import APIRouter, Depends, Query

from app.repositories.preferences_repository import PreferencesRepository, get_preferences_repository
from app.schemas.common import ApiResponse
from app.schemas.persistence import UserPreferencesModel, UserPreferencesUpdate

router = APIRouter(prefix="/preferences", tags=["User Preferences"])


@router.get("", response_model=ApiResponse[UserPreferencesModel])
async def get_user_preferences(
    user_id: str = Query("guest_user"),
    repo: PreferencesRepository = Depends(get_preferences_repository),
) -> ApiResponse[UserPreferencesModel]:
    """Retrieves current user preferences (UI theme, default exchange, chart interval, etc.)."""
    prefs = await repo.get_preferences(user_id=user_id)
    return ApiResponse(success=True, data=prefs)


@router.patch("", response_model=ApiResponse[UserPreferencesModel])
async def update_user_preferences(
    payload: UserPreferencesUpdate,
    user_id: str = Query("guest_user"),
    repo: PreferencesRepository = Depends(get_preferences_repository),
) -> ApiResponse[UserPreferencesModel]:
    """Updates selected user preferences."""
    updated = await repo.update_preferences(user_id=user_id, updates=payload)
    return ApiResponse(success=True, data=updated)
