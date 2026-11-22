"""
Learning REST Endpoints for RG AI Education Platform.
Exposes courses, syllabus, lessons, categories, search, progress, bookmarks, and quiz submissions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.learning import (
    BookmarkRequest,
    CategoryInfo,
    CourseDetail,
    CourseSummary,
    DifficultyLevel,
    LearningCategory,
    LearningSearchResponse,
    LessonDetail,
    ProgressUpdateRequest,
    QuizSubmissionRequest,
    QuizSubmissionResult,
    UserLearningProgress,
)
from app.services.learning_service import LearningService, get_learning_service

router = APIRouter(prefix="/learning", tags=["Learning & Education"])


@router.get(
    "/courses",
    response_model=List[CourseSummary],
    summary="List educational courses with optional category & difficulty filters",
)
async def list_courses(
    category: Optional[LearningCategory] = Query(default=None, description="Filter by learning category"),
    difficulty: Optional[DifficultyLevel] = Query(default=None, description="Filter by difficulty level"),
    limit: int = Query(default=50, ge=1, le=100, description="Max courses to return"),
    skip: int = Query(default=0, ge=0, description="Offset for pagination"),
    service: LearningService = Depends(get_learning_service),
):
    """Retrieve courses matching criteria."""
    courses, _ = await service.get_courses(
        category=category, difficulty=difficulty, limit=limit, skip=skip
    )
    return courses


@router.get(
    "/courses/{course_id}",
    response_model=CourseDetail,
    summary="Get complete course details and lesson syllabus",
)
async def get_course(
    course_id: str,
    service: LearningService = Depends(get_learning_service),
):
    """Fetch a course by its unique ID."""
    course = await service.get_course_detail(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID '{course_id}' was not found.",
        )
    return course


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonDetail,
    summary="Get detailed lesson content, examples, notes, and quiz",
)
async def get_lesson(
    lesson_id: str,
    service: LearningService = Depends(get_learning_service),
):
    """Fetch lesson content by ID."""
    lesson = await service.get_lesson_detail(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID '{lesson_id}' was not found.",
        )
    return lesson


@router.get(
    "/categories",
    response_model=List[CategoryInfo],
    summary="List all 14 learning categories with metadata and course counts",
)
async def list_categories(
    service: LearningService = Depends(get_learning_service),
):
    """Fetch all 14 standardized Indian Stock Market education categories."""
    return await service.get_categories()


@router.get(
    "/search",
    response_model=LearningSearchResponse,
    summary="Search educational content across courses and lessons",
)
async def search_content(
    q: str = Query(..., min_length=1, max_length=100, description="Search query keyword"),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum matches"),
    service: LearningService = Depends(get_learning_service),
):
    """Search courses and lessons by keyword."""
    return await service.search(query=q, limit=limit)


@router.get(
    "/progress",
    response_model=UserLearningProgress,
    summary="Get current user learning progress and bookmarks",
)
async def get_progress(
    user_id: str = Query(default="guest_user", description="Identifier for progress store"),
    service: LearningService = Depends(get_learning_service),
):
    """Fetch current user completed lessons, quiz scores, and bookmarks."""
    return await service.get_progress(user_id=user_id)


@router.post(
    "/progress",
    response_model=UserLearningProgress,
    summary="Update lesson completion or last accessed lesson",
)
async def update_progress(
    payload: ProgressUpdateRequest,
    user_id: str = Query(default="guest_user", description="Identifier for progress store"),
    service: LearningService = Depends(get_learning_service),
):
    """Record completion of a lesson and update course progress."""
    return await service.update_progress(
        lesson_id=payload.lesson_id,
        completed=payload.completed,
        course_id=payload.course_id,
        user_id=user_id,
    )


@router.get(
    "/bookmarks",
    response_model=List[str],
    summary="Get bookmarked lesson IDs for user",
)
async def get_bookmarks(
    user_id: str = Query(default="guest_user", description="Identifier for progress store"),
    service: LearningService = Depends(get_learning_service),
) -> List[str]:
    """Fetch user's bookmarked lesson IDs."""
    progress = await service.get_progress(user_id=user_id)
    return progress.bookmarked_lesson_ids


@router.post(
    "/bookmarks",
    response_model=UserLearningProgress,
    summary="Bookmark a lesson for quick access",
)
async def add_bookmark(
    payload: BookmarkRequest,
    user_id: str = Query(default="guest_user", description="Identifier for progress store"),
    service: LearningService = Depends(get_learning_service),
):
    """Add a lesson to the user's saved list."""
    return await service.add_bookmark(
        lesson_id=payload.lesson_id, note=payload.note, user_id=user_id
    )


@router.delete(
    "/bookmarks/{lesson_id}",
    response_model=UserLearningProgress,
    summary="Remove a lesson bookmark",
)
async def remove_bookmark(
    lesson_id: str,
    user_id: str = Query(default="guest_user", description="Identifier for progress store"),
    service: LearningService = Depends(get_learning_service),
):
    """Remove a lesson from the user's saved list."""
    return await service.remove_bookmark(lesson_id=lesson_id, user_id=user_id)


@router.post(
    "/quizzes/{quiz_id}/submit",
    response_model=QuizSubmissionResult,
    summary="Submit quiz answers for deterministic backend grading",
)
async def submit_quiz(
    quiz_id: str,
    payload: QuizSubmissionRequest,
    user_id: str = Query(default="guest_user", description="Identifier for progress store"),
    service: LearningService = Depends(get_learning_service),
):
    """
    Deterministically grades submitted quiz answers against internal answer key.
    Calculates score percentage and returns per-question explanations.
    """
    result = await service.evaluate_quiz(
        quiz_id=quiz_id, answers=payload.answers, user_id=user_id
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID '{quiz_id}' was not found.",
        )
    return result
