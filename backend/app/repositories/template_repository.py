"""
Template Repository for RG AI.
Provides MongoDB persistence and fallback for prompt templates used by the AI engine.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

from app.core.database import database_manager
from app.repositories.base import BaseRepository
from app.schemas.persistence import PromptTemplateModel, PromptTemplateCreate
from app.integrations.rg_ai.prompt_templates import _TEMPLATES

logger = logging.getLogger(__name__)


class TemplateRepository(BaseRepository[PromptTemplateModel]):
    """Repository managing versioned prompt templates in MongoDB."""

    def __init__(self) -> None:
        super().__init__(collection_name="prompt_templates")
        self._memory_store: Dict[str, PromptTemplateModel] = {}

        self._seed_in_memory()

    def _seed_in_memory(self) -> None:
        """Seeds the 10 Phase 5 prompt templates in memory."""
        now = datetime.now(timezone.utc)
        for key, t in _TEMPLATES.items():
            model = PromptTemplateModel(
                template_id=t.template_id,
                name=t.name,
                target_schema_type=t.target_schema_type,
                version=t.version,
                instructions=t.instructions,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            self._memory_store[t.template_id] = model

    async def seed_mongodb(self) -> int:
        """Seeds prompt templates to MongoDB if collection is empty."""
        if not self.is_available:
            return 0
        try:
            col = self.collection
            count = await col.count_documents({})
            if count > 0:
                return count
            
            inserted = 0
            for model in self._memory_store.values():
                await col.update_one(
                    {"template_id": model.template_id},
                    {"$setOnInsert": model.model_dump()},
                    upsert=True,
                )
                inserted += 1
            return inserted
        except Exception as e:
            logger.warning(f"Failed to seed prompt templates in MongoDB: {e}")
            return 0

    async def get_by_template_id(self, template_id: str) -> Optional[PromptTemplateModel]:
        """Fetches template by unique template_id."""
        if self.is_available:
            doc = await self.find_one({"template_id": template_id})
            if doc:
                return doc
        return self._memory_store.get(template_id)

    async def list_templates(
        self,
        active_only: bool = True,
        limit: int = 50,
        skip: int = 0,
    ) -> Tuple[List[PromptTemplateModel], int]:
        """Lists available prompt templates."""
        filter_query = {"is_active": True} if active_only else {}
        if self.is_available:
            try:
                items = await self.find_many(filter_query, limit=limit, skip=skip, sort=[("name", 1)])
                total = await self.count(filter_query)
                if items:
                    return items, total
            except Exception as e:
                logger.warning(f"Error reading prompt templates from MongoDB: {e}")

        # Fallback to in-memory store
        all_items = [
            t for t in self._memory_store.values()
            if not active_only or t.is_active
        ]
        all_items.sort(key=lambda x: x.name)
        return all_items[skip : skip + limit], len(all_items)

    async def upsert_template(self, payload: PromptTemplateCreate) -> PromptTemplateModel:
        """Inserts or updates a prompt template."""
        now = datetime.now(timezone.utc)
        existing = await self.get_by_template_id(payload.template_id)

        model = PromptTemplateModel(
            template_id=payload.template_id,
            name=payload.name,
            target_schema_type=payload.target_schema_type,
            version=payload.version,
            instructions=payload.instructions,
            is_active=payload.is_active,
            created_at=existing.created_at if existing else now,
            updated_at=now,
        )

        self._memory_store[payload.template_id] = model

        if self.is_available:
            try:
                await self.collection.update_one(
                    {"template_id": payload.template_id},
                    {"$set": model.model_dump()},
                    upsert=True,
                )
            except Exception as e:
                logger.error(f"Error persisting template {payload.template_id} to MongoDB: {e}")

        return model


_template_repository: Optional[TemplateRepository] = None


def get_template_repository() -> TemplateRepository:
    """Singleton getter for TemplateRepository."""
    global _template_repository
    if _template_repository is None:
        _template_repository = TemplateRepository()
    return _template_repository
