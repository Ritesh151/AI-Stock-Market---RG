"""
Learning Repository Interface and In-Memory Implementation.
Houses the curated Indian Stock Market curriculum across 14 categories,
3 difficulty levels, 13 candlestick patterns, indicators, quizzes, and user progress.
Prepared for Phase 10 MongoDB database integration.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import copy

from app.schemas.learning import (
    CategoryInfo,
    CourseDetail,
    CourseSummary,
    DifficultyLevel,
    LearningCategory,
    LessonDetail,
    LessonExample,
    LessonSummary,
    QuestionType,
    QuizAnswerSubmission,
    QuizOption,
    QuizPublic,
    QuizQuestionInternal,
    QuizQuestionPublic,
    QuizSubmissionResult,
    QuestionFeedback,
    UserLearningProgress,
)


class LearningRepository(ABC):
    """Abstract repository contract for learning content and progress persistence."""

    @abstractmethod
    async def get_courses(
        self,
        category: Optional[LearningCategory] = None,
        difficulty: Optional[DifficultyLevel] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> Tuple[List[CourseSummary], int]:
        """Fetch list of courses with optional filters and total count."""
        pass

    @abstractmethod
    async def get_course_by_id(self, course_id: str) -> Optional[CourseDetail]:
        """Fetch course details with lesson syllabus."""
        pass

    @abstractmethod
    async def get_lesson_by_id(self, lesson_id: str) -> Optional[LessonDetail]:
        """Fetch full lesson content and inline quiz."""
        pass

    @abstractmethod
    async def get_categories(self) -> List[CategoryInfo]:
        """Fetch all 14 categories with counts."""
        pass

    @abstractmethod
    async def search_content(
        self, query: str, limit: int = 20
    ) -> Tuple[List[CourseSummary], List[LessonSummary]]:
        """Search courses and lessons by keyword."""
        pass

    @abstractmethod
    async def get_user_progress(self, user_id: str = "guest_user") -> UserLearningProgress:
        """Fetch user progress."""
        pass

    @abstractmethod
    async def update_user_progress(
        self,
        lesson_id: str,
        completed: bool = True,
        course_id: Optional[str] = None,
        user_id: str = "guest_user",
    ) -> UserLearningProgress:
        """Record lesson completion or opening."""
        pass

    @abstractmethod
    async def add_bookmark(
        self, lesson_id: str, note: Optional[str] = None, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        """Bookmark a lesson."""
        pass

    @abstractmethod
    async def remove_bookmark(
        self, lesson_id: str, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        """Remove a lesson bookmark."""
        pass

    @abstractmethod
    async def evaluate_quiz(
        self,
        quiz_id: str,
        answers: List[QuizAnswerSubmission],
        user_id: str = "guest_user",
    ) -> Optional[QuizSubmissionResult]:
        """Deterministically evaluate quiz answers against internal answer key."""
        pass


class InMemoryLearningRepository(LearningRepository):
    """
    In-memory implementation pre-seeded with structured educational content.
    Thread-safe for development and testing.
    """

    def __init__(self):
        self._courses: Dict[str, CourseDetail] = {}
        self._lessons: Dict[str, LessonDetail] = {}
        self._quizzes: Dict[str, List[QuizQuestionInternal]] = {}
        self._quiz_metadata: Dict[str, Dict[str, Any]] = {}
        self._user_progress: Dict[str, UserLearningProgress] = {}
        self._seed_curriculum()

    def _seed_curriculum(self):
        """Seed rich, verified curriculum content for all 14 categories and levels."""
        from app.repositories.curriculum_data import (
            COURSES_DATA,
            LESSONS_DATA,
            QUIZZES_DATA,
        )

        for course in COURSES_DATA:
            self._courses[course.id] = course

        for lesson in LESSONS_DATA:
            self._lessons[lesson.id] = lesson

        for q_id, q_data in QUIZZES_DATA.items():
            self._quizzes[q_id] = q_data["questions"]
            self._quiz_metadata[q_id] = {
                "title": q_data["title"],
                "lesson_id": q_data["lesson_id"],
                "passing_score": q_data.get("passing_score", 70),
            }

    async def get_courses(
        self,
        category: Optional[LearningCategory] = None,
        difficulty: Optional[DifficultyLevel] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> Tuple[List[CourseSummary], int]:
        filtered = list(self._courses.values())

        if category:
            filtered = [c for c in filtered if c.category == category]
        if difficulty:
            filtered = [c for c in filtered if c.difficulty == difficulty]

        total = len(filtered)
        paged = filtered[skip : skip + limit]

        # Convert to summaries
        summaries = [
            CourseSummary(
                id=c.id,
                title=c.title,
                description=c.description,
                difficulty=c.difficulty,
                category=c.category,
                estimated_duration=c.estimated_duration,
                lesson_count=c.lesson_count,
                learning_objectives=c.learning_objectives,
                prerequisites=c.prerequisites,
            )
            for c in paged
        ]
        return summaries, total

    async def get_course_by_id(self, course_id: str) -> Optional[CourseDetail]:
        course = self._courses.get(course_id)
        if not course:
            return None
        return copy.deepcopy(course)

    async def get_lesson_by_id(self, lesson_id: str) -> Optional[LessonDetail]:
        lesson = self._lessons.get(lesson_id)
        if not lesson:
            return None

        # Build public version of quiz if quiz exists
        lesson_copy = copy.deepcopy(lesson)
        quiz_id = f"quiz-{lesson_id}"
        if quiz_id in self._quizzes:
            meta = self._quiz_metadata.get(quiz_id, {})
            internal_questions = self._quizzes[quiz_id]
            public_questions = [
                QuizQuestionPublic(
                    id=q.id,
                    question=q.question,
                    question_type=q.question_type,
                    options=q.options,
                    scenario_context=q.scenario_context,
                    illustration_key=q.illustration_key,
                )
                for q in internal_questions
            ]
            lesson_copy.quiz = QuizPublic(
                id=quiz_id,
                lesson_id=lesson_id,
                title=meta.get("title", f"Knowledge Check: {lesson.title}"),
                questions=public_questions,
                passing_score_percent=meta.get("passing_score", 70),
            )

        return lesson_copy

    async def get_categories(self) -> List[CategoryInfo]:
        counts: Dict[LearningCategory, Dict[str, Any]] = {}
        for cat in LearningCategory:
            counts[cat] = {
                "course_count": 0,
                "lesson_count": 0,
                "primary_level": DifficultyLevel.BEGINNER,
            }

        for course in self._courses.values():
            if course.category in counts:
                counts[course.category]["course_count"] += 1
                counts[course.category]["primary_level"] = course.difficulty

        for lesson in self._lessons.values():
            if lesson.category in counts:
                counts[lesson.category]["lesson_count"] += 1

        descriptions = {
            LearningCategory.STOCK_MARKET_BASICS: "Foundations of Indian equity markets, exchanges (NSE/BSE), and accounts.",
            LearningCategory.CANDLESTICK_PATTERNS: "Identification and interpretation of 13 primary reversal and continuation candles.",
            LearningCategory.TECHNICAL_ANALYSIS: "Chart reading, Dow theory, trends, and multi-timeframe principles.",
            LearningCategory.FUNDAMENTAL_ANALYSIS: "Financial statement basics, valuation metrics (P/E, P/B, ROE), and moat analysis.",
            LearningCategory.SUPPORT_AND_RESISTANCE: "Identifying institutional demand/supply zones, trendlines, and role reversal.",
            LearningCategory.RSI_INDICATOR: "Relative Strength Index momentum, oversold/overbought nuances, and divergences.",
            LearningCategory.MACD_INDICATOR: "Moving Average Convergence Divergence line, signal line, and histogram dynamics.",
            LearningCategory.MOVING_AVERAGES: "SMA, EMA, Golden Cross, Death Cross, and dynamic trend tracking.",
            LearningCategory.VOLUME_ANALYSIS: "Volume price confirmation, institutional footprints, and fakeout detection.",
            LearningCategory.RISK_MANAGEMENT: "1% rule, capital preservation, position sizing formulas, and stop-loss placement.",
            LearningCategory.TRADING_PSYCHOLOGY: "Emotional discipline, FOMO prevention, revenge trading mitigation, and consistency.",
            LearningCategory.SWING_TRADING: "Multi-day price swing setups, pullback trading, and catalyst positioning.",
            LearningCategory.LONG_TERM_INVESTING: "Compounding, asset allocation, index fund investing, and wealth creation principles.",
            LearningCategory.PORTFOLIO_MANAGEMENT: "Diversification, sector rotation, rebalancing, and correlation risk.",
        }

        result = []
        for cat in LearningCategory:
            info = counts[cat]
            result.append(
                CategoryInfo(
                    name=cat,
                    description=descriptions.get(cat, f"Comprehensive lessons on {cat.value}."),
                    course_count=info["course_count"],
                    lesson_count=info["lesson_count"],
                    primary_level=info["primary_level"],
                )
            )
        return result

    async def search_content(
        self, query: str, limit: int = 20
    ) -> Tuple[List[CourseSummary], List[LessonSummary]]:
        q = query.lower().strip()
        if not q:
            return [], []

        matching_courses: List[CourseSummary] = []
        for c in self._courses.values():
            if (
                q in c.title.lower()
                or q in c.description.lower()
                or q in c.category.value.lower()
            ):
                matching_courses.append(
                    CourseSummary(
                        id=c.id,
                        title=c.title,
                        description=c.description,
                        difficulty=c.difficulty,
                        category=c.category,
                        estimated_duration=c.estimated_duration,
                        lesson_count=c.lesson_count,
                        learning_objectives=c.learning_objectives,
                        prerequisites=c.prerequisites,
                    )
                )

        matching_lessons: List[LessonSummary] = []
        for l in self._lessons.values():
            if (
                q in l.title.lower()
                or q in l.explanation.lower()
                or any(q in k.lower() for k in l.key_concepts)
                or q in l.category.value.lower()
            ):
                matching_lessons.append(
                    LessonSummary(
                        id=l.id,
                        course_id=l.course_id,
                        title=l.title,
                        order=l.order,
                        duration=l.duration,
                        category=l.category,
                        difficulty=l.difficulty,
                    )
                )

        return matching_courses[:limit], matching_lessons[:limit]

    async def get_user_progress(self, user_id: str = "guest_user") -> UserLearningProgress:
        if user_id not in self._user_progress:
            self._user_progress[user_id] = UserLearningProgress(user_id=user_id)
        return copy.deepcopy(self._user_progress[user_id])

    async def update_user_progress(
        self,
        lesson_id: str,
        completed: bool = True,
        course_id: Optional[str] = None,
        user_id: str = "guest_user",
    ) -> UserLearningProgress:
        progress = await self.get_user_progress(user_id)

        # Update last accessed
        progress.last_accessed_lesson_id = lesson_id
        if course_id:
            progress.last_accessed_course_id = course_id
            if course_id not in progress.in_progress_course_ids:
                progress.in_progress_course_ids.append(course_id)

        if completed and lesson_id not in progress.completed_lesson_ids:
            progress.completed_lesson_ids.append(lesson_id)

        # Check if course is fully completed
        if course_id and course_id in self._courses:
            course = self._courses[course_id]
            course_lesson_ids = [l.id for l in course.lessons]
            if course_lesson_ids and all(
                lid in progress.completed_lesson_ids for lid in course_lesson_ids
            ):
                if course_id not in progress.completed_course_ids:
                    progress.completed_course_ids.append(course_id)

        progress.updated_at = datetime.now(timezone.utc)
        self._user_progress[user_id] = progress
        return copy.deepcopy(progress)

    async def add_bookmark(
        self, lesson_id: str, note: Optional[str] = None, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        progress = await self.get_user_progress(user_id)
        if lesson_id not in progress.bookmarked_lesson_ids:
            progress.bookmarked_lesson_ids.append(lesson_id)
        progress.updated_at = datetime.now(timezone.utc)
        self._user_progress[user_id] = progress
        return copy.deepcopy(progress)

    async def remove_bookmark(
        self, lesson_id: str, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        progress = await self.get_user_progress(user_id)
        if lesson_id in progress.bookmarked_lesson_ids:
            progress.bookmarked_lesson_ids.remove(lesson_id)
        progress.updated_at = datetime.now(timezone.utc)
        self._user_progress[user_id] = progress
        return copy.deepcopy(progress)

    async def evaluate_quiz(
        self,
        quiz_id: str,
        answers: List[QuizAnswerSubmission],
        user_id: str = "guest_user",
    ) -> Optional[QuizSubmissionResult]:
        if quiz_id not in self._quizzes:
            return None

        internal_questions = self._quizzes[quiz_id]
        question_map = {q.id: q for q in internal_questions}
        answers_map = {a.question_id: a.selected_option_id for a in answers}

        feedback_list: List[QuestionFeedback] = []
        correct_count = 0

        for q in internal_questions:
            user_choice = answers_map.get(q.id, "")
            is_correct = user_choice == q.correct_option_id
            if is_correct:
                correct_count += 1

            feedback_list.append(
                QuestionFeedback(
                    question_id=q.id,
                    selected_option_id=user_choice,
                    correct_option_id=q.correct_option_id,
                    is_correct=is_correct,
                    explanation=q.explanation,
                )
            )

        total_questions = len(internal_questions)
        score_percentage = (
            round((correct_count / total_questions) * 100.0, 1)
            if total_questions > 0
            else 0.0
        )
        meta = self._quiz_metadata.get(quiz_id, {})
        passing_score = meta.get("passing_score", 70)
        passed = score_percentage >= passing_score

        # Record quiz score in user progress
        progress = await self.get_user_progress(user_id)
        current_best = progress.quiz_scores.get(quiz_id, 0.0)
        if score_percentage > current_best:
            progress.quiz_scores[quiz_id] = score_percentage
            progress.updated_at = datetime.now(timezone.utc)
            self._user_progress[user_id] = progress

        return QuizSubmissionResult(
            quiz_id=quiz_id,
            total_questions=total_questions,
            correct_count=correct_count,
            score_percentage=score_percentage,
            passed=passed,
            feedback=feedback_list,
        )



import logging
from app.core.database import database_manager

logger = logging.getLogger(__name__)


class MongoLearningRepository(InMemoryLearningRepository):
    """
    MongoDB-backed Learning Repository with resilient in-memory fallback.
    Persists user progress, bookmarks, and quiz attempts to MongoDB collections:
    'learning_progress', 'learning_bookmarks', and 'quiz_attempts'.
    """

    def __init__(self) -> None:
        super().__init__()
        self.progress_collection_name = "learning_progress"
        self.bookmarks_collection_name = "learning_bookmarks"
        self.quiz_collection_name = "quiz_attempts"

    @property
    def is_available(self) -> bool:
        return database_manager.is_connected

    async def get_user_progress(self, user_id: str = "guest_user") -> UserLearningProgress:
        if self.is_available:
            try:
                db = database_manager.get_database()
                doc = await db[self.progress_collection_name].find_one({"user_id": user_id})
                if doc:
                    doc.pop("_id", None)
                    progress = UserLearningProgress(**doc)
                    self._user_progress[user_id] = progress
                    return copy.deepcopy(progress)
            except Exception as e:
                logger.warning(f"Failed to fetch user progress from MongoDB: {e}")
        return await super().get_user_progress(user_id)

    async def update_user_progress(
        self,
        lesson_id: str,
        completed: bool = True,
        course_id: Optional[str] = None,
        user_id: str = "guest_user",
    ) -> UserLearningProgress:
        progress = await super().update_user_progress(lesson_id, completed, course_id, user_id)
        if self.is_available:
            try:
                db = database_manager.get_database()
                await db[self.progress_collection_name].update_one(
                    {"user_id": user_id},
                    {"$set": progress.model_dump()},
                    upsert=True,
                )
            except Exception as e:
                logger.warning(f"Failed to persist user progress to MongoDB: {e}")
        return progress

    async def add_bookmark(
        self, lesson_id: str, note: Optional[str] = None, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        progress = await super().add_bookmark(lesson_id, note, user_id)
        if self.is_available:
            try:
                db = database_manager.get_database()
                await db[self.progress_collection_name].update_one(
                    {"user_id": user_id},
                    {"$set": progress.model_dump()},
                    upsert=True,
                )
                await db[self.bookmarks_collection_name].update_one(
                    {"user_id": user_id, "lesson_id": lesson_id},
                    {
                        "$set": {
                            "user_id": user_id,
                            "lesson_id": lesson_id,
                            "note": note,
                            "created_at": datetime.now(timezone.utc),
                        }
                    },
                    upsert=True,
                )
            except Exception as e:
                logger.warning(f"Failed to persist bookmark to MongoDB: {e}")
        return progress

    async def remove_bookmark(
        self, lesson_id: str, user_id: str = "guest_user"
    ) -> UserLearningProgress:
        progress = await super().remove_bookmark(lesson_id, user_id)
        if self.is_available:
            try:
                db = database_manager.get_database()
                await db[self.progress_collection_name].update_one(
                    {"user_id": user_id},
                    {"$set": progress.model_dump()},
                    upsert=True,
                )
                await db[self.bookmarks_collection_name].delete_one(
                    {"user_id": user_id, "lesson_id": lesson_id}
                )
            except Exception as e:
                logger.warning(f"Failed to delete bookmark from MongoDB: {e}")
        return progress

    async def evaluate_quiz(
        self,
        quiz_id: str,
        answers: List[QuizAnswerSubmission],
        user_id: str = "guest_user",
    ) -> Optional[QuizSubmissionResult]:
        result = await super().evaluate_quiz(quiz_id, answers, user_id)
        if result and self.is_available:
            try:
                db = database_manager.get_database()
                progress = await self.get_user_progress(user_id)
                await db[self.progress_collection_name].update_one(
                    {"user_id": user_id},
                    {"$set": progress.model_dump()},
                    upsert=True,
                )
                attempt_doc = {
                    "user_id": user_id,
                    "quiz_id": quiz_id,
                    "total_questions": result.total_questions,
                    "correct_count": result.correct_count,
                    "score_percentage": result.score_percentage,
                    "passed": result.passed,
                    "submitted_at": datetime.now(timezone.utc),
                }
                await db[self.quiz_collection_name].insert_one(attempt_doc)
            except Exception as e:
                logger.warning(f"Failed to record quiz attempt in MongoDB: {e}")
        return result


# Singleton instance helper
_learning_repository: Optional[LearningRepository] = None


def get_learning_repository() -> LearningRepository:
    """Provides singleton access to the active LearningRepository."""
    global _learning_repository
    if _learning_repository is None:
        _learning_repository = MongoLearningRepository()
    return _learning_repository


def set_learning_repository(repo: LearningRepository) -> None:
    """Allows injecting custom repository during testing or migration."""
    global _learning_repository
    _learning_repository = repo

