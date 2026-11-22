"""
Saved Analyses API Endpoints for RG AI.
Provides complete CRUD persistence for user-saved financial analysis reports in MongoDB.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.repositories.analysis_repository import AnalysisRepository, get_analysis_repository
from app.schemas.common import ApiResponse
from app.schemas.persistence import SavedAnalysisCreate, SavedAnalysisModel

router = APIRouter(prefix="/analyses", tags=["Saved Analyses"])


@router.get("", response_model=ApiResponse[List[SavedAnalysisModel]])
async def list_saved_analyses(
    symbol: Optional[str] = Query(None, description="Optional stock symbol filter"),
    analysis_type: Optional[str] = Query(None, description="Optional analysis type filter"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    user_id: str = Query("guest_user"),
    repo: AnalysisRepository = Depends(get_analysis_repository),
) -> ApiResponse[List[SavedAnalysisModel]]:
    """Lists saved financial analyses for the specified user."""
    items = await repo.list_analyses(
        user_id=user_id,
        symbol=symbol,
        analysis_type=analysis_type,
        limit=limit,
        skip=skip,
    )
    return ApiResponse(success=True, data=items)


@router.post("", response_model=ApiResponse[SavedAnalysisModel], status_code=status.HTTP_201_CREATED)
async def save_analysis(
    payload: SavedAnalysisCreate,
    user_id: str = Query("guest_user"),
    repo: AnalysisRepository = Depends(get_analysis_repository),
) -> ApiResponse[SavedAnalysisModel]:
    """Persists a validated financial analysis report."""
    saved = await repo.save_analysis(user_id=user_id, payload=payload)
    return ApiResponse(success=True, data=saved)


@router.get("/{analysis_id}", response_model=ApiResponse[SavedAnalysisModel])
async def get_saved_analysis(
    analysis_id: str,
    user_id: str = Query("guest_user"),
    repo: AnalysisRepository = Depends(get_analysis_repository),
) -> ApiResponse[SavedAnalysisModel]:
    """Retrieves a single saved analysis report by ID."""
    item = await repo.get_analysis(user_id=user_id, analysis_id=analysis_id)
    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return ApiResponse(success=True, data=item)


@router.delete("/{analysis_id}", response_model=ApiResponse[dict])
async def delete_saved_analysis(
    analysis_id: str,
    user_id: str = Query("guest_user"),
    repo: AnalysisRepository = Depends(get_analysis_repository),
) -> ApiResponse[dict]:
    """Deletes a saved analysis report."""
    deleted = await repo.delete_analysis(user_id=user_id, analysis_id=analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return ApiResponse(success=True, data={"deleted": True, "analysis_id": analysis_id})
