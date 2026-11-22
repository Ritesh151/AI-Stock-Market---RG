"""
Saved Analysis Repository for MongoDB.
Stores validated RG AI financial analysis outputs with schema versions and source attribution.
"""

from datetime import datetime, timezone
import uuid
from typing import Dict, List, Optional
from pymongo import DESCENDING

from app.core.logging import get_logger
from app.repositories.base import BaseRepository
from app.schemas.persistence import SavedAnalysisCreate, SavedAnalysisModel

logger = get_logger("analysis_repo")


class AnalysisRepository(BaseRepository[SavedAnalysisModel]):
    """Repository handling saved stock analysis persistence."""

    def __init__(self):
        super().__init__(collection_name="saved_analyses")
        self._fallback_store: Dict[str, SavedAnalysisModel] = {}

    async def save_analysis(
        self, user_id: str, payload: SavedAnalysisCreate
    ) -> SavedAnalysisModel:
        """Save a validated financial analysis."""
        analysis_id = f"anl_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        model = SavedAnalysisModel(
            analysis_id=analysis_id,
            user_id=user_id,
            conversation_id=payload.conversation_id,
            symbol=payload.symbol.upper().strip(),
            exchange=payload.exchange.upper().strip(),
            analysis_type=payload.analysis_type,
            validated_data=payload.validated_data,
            schema_version=payload.schema_version,
            data_source=payload.data_source or "RG AI Intelligence Engine",
            created_at=now,
        )

        if self.is_available and self.collection is not None:
            await self.collection.insert_one(model.model_dump())
        else:
            self._fallback_store[analysis_id] = model

        return model

    async def get_analysis(
        self, user_id: str, analysis_id: str
    ) -> Optional[SavedAnalysisModel]:
        """Fetch saved analysis strictly checking user ownership."""
        if self.is_available and self.collection is not None:
            doc = await self.collection.find_one(
                {"user_id": user_id, "analysis_id": analysis_id}
            )
            if doc:
                doc.pop("_id", None)
                return SavedAnalysisModel(**doc)
            return None

        anl = self._fallback_store.get(analysis_id)
        if anl and anl.user_id == user_id:
            return anl
        return None

    async def list_analyses(
        self,
        user_id: str,
        symbol: Optional[str] = None,
        analysis_type: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> List[SavedAnalysisModel]:
        """List saved analyses for a user with optional symbol and type filters."""
        if self.is_available and self.collection is not None:
            query = {"user_id": user_id}
            if symbol and symbol.strip():
                query["symbol"] = symbol.upper().strip()
            if analysis_type and analysis_type.strip():
                query["analysis_type"] = analysis_type.strip()

            cursor = (
                self.collection.find(query)
                .sort("created_at", DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            results = []
            async for doc in cursor:
                doc.pop("_id", None)
                results.append(SavedAnalysisModel(**doc))
            return results

        # In-memory fallback
        items = [a for a in self._fallback_store.values() if a.user_id == user_id]
        if symbol:
            items = [a for a in items if a.symbol == symbol.upper().strip()]
        if analysis_type:
            items = [a for a in items if a.analysis_type == analysis_type]
        items.sort(key=lambda a: a.created_at, reverse=True)
        return items[skip : skip + limit]

    async def delete_analysis(self, user_id: str, analysis_id: str) -> bool:
        """Delete a saved analysis strictly verifying ownership."""
        if self.is_available and self.collection is not None:
            res = await self.collection.delete_one(
                {"user_id": user_id, "analysis_id": analysis_id}
            )
            return res.deleted_count > 0

        anl = self._fallback_store.get(analysis_id)
        if anl and anl.user_id == user_id:
            del self._fallback_store[analysis_id]
            return True
        return False


_analysis_repository: Optional[AnalysisRepository] = None


def get_analysis_repository() -> AnalysisRepository:
    """Singleton getter for AnalysisRepository."""
    global _analysis_repository
    if _analysis_repository is None:
        _analysis_repository = AnalysisRepository()
    return _analysis_repository
