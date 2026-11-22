"""
Learning Service for RG AI Education Platform.
Provides business orchestration for course syllabus, lesson viewer,
search/filtering, deterministic quiz scoring, and user progress management.
"""

from typing import Dict, List, Optional, Tuple
from app.repositories.learning_repository import (
    LearningRepository,
    get_learning_repository,
)
from app.schemas.learning import (
    CategoryInfo,
    CourseDetail,
    CourseSummary,
    DifficultyLevel,
    LearningCategory,
    LearningSearchResponse,
    LessonDetail,
    LessonSummary,
    QuizAnswerSubmission,
    QuizSubmissionResult,
    UserLearningProgress,
)


class LearningService:
    """Service layer for learning platform operations."""

    def __init__(self, repository: Optional[LearningRepository] = None):
        self._repo = repository or get_learning_repository()

    async def get_courses(
        self,
        category: Optional[LearningCategory] = None,
        difficulty: Optional[DifficultyLevel] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> Tuple[List[CourseSummary], int]:
        """Fetch courses with category and difficulty filters."""
        return await self._repo.get_courses(
            category=category, difficulty=difficulty, limit=limit, skip=skip
        )

    async def get_course_detail(self, course_id: str) -> Optional[CourseDetail]:
        """Fetch complete course syllabus by ID."""
        return await self._repo.get_course_by_id(course_id)

    async def get_lesson_detail(self, lesson_id: str) -> Optional[LessonDetail]:
        """Fetch lesson content, examples, notes, and quiz by ID."""
        return await self._repo.get_lesson_by_id(lesson_id)

    async def get_categories(self) -> List[CategoryInfo]:
        """Fetch all 14 categories with active course counts."""
        return await self._repo.get_categories()

    async def search(self, query: str, limit: int = 20) -> LearningSearchResponse:
        """Search across courses and lessons."""
        courses, lessons = await self._repo.search_content(query=query, limit=limit)
        return LearningSearchResponse(
            query=query,
            total_results=len(courses) + len(lessons),
            courses=courses,
            lessons=lessons,
        )

    async def get_progress(self, user_id: str = "guest_user") -> UserLearningProgress:
        """Fetch current user learning progress."""
        return await self._repo.get_user_progress(user_id=user_id)

    async def update_progress(
        self,
        lesson_id: str,
        completed: bool = True,
        course_id: Optional[str] = None,
        user_id: str = "guest_user",
    ) -> UserLearningProgress:
        """Update progress for a specific lesson and course."""
        return await self._repo.update_user_progress(
            lesson_id=lesson_id,
            completed=completed,
            course_id=course_id,
            user_id=user_id,
        )

    async def add_bookmark(
        self, lesson_id: str, note: Optional[str] = None, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        """Add a lesson to user bookmarks."""
        return await self._repo.add_bookmark(
            lesson_id=lesson_id, note=note, user_id=user_id
        )

    async def remove_bookmark(
        self, lesson_id: str, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        """Remove a lesson from user bookmarks."""
        return await self._repo.remove_bookmark(lesson_id=lesson_id, user_id=user_id)

    async def evaluate_quiz(
        self,
        quiz_id: str,
        answers: List[QuizAnswerSubmission],
        user_id: str = "guest_user",
    ) -> Optional[QuizSubmissionResult]:
        """Grade a quiz submission deterministically."""
        return await self._repo.evaluate_quiz(
            quiz_id=quiz_id, answers=answers, user_id=user_id
        )


# Singleton instance
_learning_service: Optional[LearningService] = None


def get_learning_service() -> LearningService:
    """Provides singleton access to LearningService."""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService()
    return _learning_service
