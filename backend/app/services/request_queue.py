"""
RG AI Async Request Queue.
Provides async-safe bounded queuing, duplicate detection, and FIFO ordering.
"""

import asyncio
import hashlib
from typing import Dict, List, Optional, Set
from app.integrations.rg_ai.gpt_config import DEFAULT_QUEUE_SIZE
from app.integrations.rg_ai.integration_exceptions import DuplicateRequestError, QueueFullError
from app.core.logging import get_logger

logger = get_logger("services.request_queue")


class QueuedItem:
    """Item held in the async execution queue."""

    def __init__(self, request_id: str, prompt_hash: str) -> None:
        self.request_id = request_id
        self.prompt_hash = prompt_hash


class RequestQueue:
    """Async-safe bounded FIFO queue with duplicate protection and position tracking."""

    def __init__(self, maxsize: int = DEFAULT_QUEUE_SIZE) -> None:
        self.maxsize = maxsize
        self._queue: asyncio.Queue[QueuedItem] = asyncio.Queue(maxsize=maxsize)
        self._active_hashes: Set[str] = set()
        self._queued_ids: List[str] = []
        self._lock = asyncio.Lock()

    @staticmethod
    def compute_prompt_hash(prompt_text: str) -> str:
        """Generates SHA-256 digest of normalized prompt to detect duplicate requests."""
        normalized = " ".join(prompt_text.strip().lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    async def enqueue(self, request_id: str, prompt_text: str) -> int:
        """
        Enqueues a request ID with duplicate protection.
        Returns the 1-indexed position in the queue.
        Raises QueueFullError if capacity exceeded.
        Raises DuplicateRequestError if identical prompt is already queued.
        """
        async with self._lock:
            if self._queue.full():
                logger.warning(f"Rejecting request {request_id}: queue full ({self._queue.qsize()}/{self.maxsize})")
                raise QueueFullError(f"Request queue is full (capacity: {self.maxsize}).")

            prompt_hash = self.compute_prompt_hash(prompt_text)
            if prompt_hash in self._active_hashes:
                logger.warning(f"Rejecting duplicate request {request_id} for prompt hash {prompt_hash[:8]}")
                raise DuplicateRequestError("An identical prompt is already queued or processing.")

            item = QueuedItem(request_id=request_id, prompt_hash=prompt_hash)
            self._queue.put_nowait(item)
            self._active_hashes.add(prompt_hash)
            self._queued_ids.append(request_id)

            position = len(self._queued_ids)
            logger.debug(f"Enqueued request {request_id} at position {position}")
            return position

    async def dequeue(self) -> QueuedItem:
        """Pulls the next queued item in FIFO order."""
        item = await self._queue.get()
        async with self._lock:
            if item.request_id in self._queued_ids:
                self._queued_ids.remove(item.request_id)
        return item

    async def release_prompt_hash(self, prompt_hash: str) -> None:
        """Releases the prompt hash so subsequent identical prompts can be accepted."""
        async with self._lock:
            self._active_hashes.discard(prompt_hash)

    async def get_position(self, request_id: str) -> Optional[int]:
        """Returns 1-indexed position of request in the queue, or None if not queued."""
        async with self._lock:
            try:
                return self._queued_ids.index(request_id) + 1
            except ValueError:
                return None

    def size(self) -> int:
        """Returns current number of queued items."""
        return self._queue.qsize()

    def is_full(self) -> bool:
        """Checks if queue is at maximum capacity."""
        return self._queue.full()

    async def clear(self) -> None:
        """Clears all queued items and resets tracking."""
        async with self._lock:
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            self._active_hashes.clear()
            self._queued_ids.clear()
