"""
Pydantic Schemas for RG AI Learn Trading Education Platform.
Defines data structures for courses, lessons, quizzes, progress, and bookmarks.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DifficultyLevel(str, Enum):
    """Trading education difficulty tiers."""
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class LearningCategory(str, Enum):
    """The 14 standardized learning categories."""
    STOCK_MARKET_BASICS = "Stock Market Basics"
    CANDLESTICK_PATTERNS = "Candlestick Patterns"
    TECHNICAL_ANALYSIS = "Technical Analysis"
    FUNDAMENTAL_ANALYSIS = "Fundamental Analysis"
    SUPPORT_AND_RESISTANCE = "Support and Resistance"
    RSI_INDICATOR = "RSI Indicator"
    MACD_INDICATOR = "MACD Indicator"
    MOVING_AVERAGES = "Moving Averages"
    VOLUME_ANALYSIS = "Volume Analysis"
    RISK_MANAGEMENT = "Risk Management"
    TRADING_PSYCHOLOGY = "Trading Psychology"
    SWING_TRADING = "Swing Trading"
    LONG_TERM_INVESTING = "Long-Term Investing"
    PORTFOLIO_MANAGEMENT = "Portfolio Management"


class QuestionType(str, Enum):
    """Quiz question variations."""
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"
    CANDLESTICK_IDENTIFY = "CANDLESTICK_IDENTIFY"
    CONCEPT_IDENTIFY = "CONCEPT_IDENTIFY"
    SCENARIO_BASED = "SCENARIO_BASED"


# =====================================================================
# Quiz Models
# =====================================================================

class QuizOption(BaseModel):
    """An option within a quiz question."""
    id: str = Field(description="Unique option identifier (e.g. 'opt-a')")
    text: str = Field(description="Display text of the option")


class QuizQuestionPublic(BaseModel):
    """Public question model sent to the client (omits correct_option_id)."""
    id: str = Field(description="Question identifier")
    question: str = Field(description="The question prompt")
    question_type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE)
    options: List[QuizOption] = Field(description="Possible choices")
    scenario_context: Optional[str] = Field(default=None, description="Contextual market background if scenario-based")
    illustration_key: Optional[str] = Field(default=None, description="SVG illustration key if applicable")


class QuizQuestionInternal(QuizQuestionPublic):
    """Internal question model containing deterministic answer key and explanation."""
    correct_option_id: str = Field(description="The correct option ID")
    explanation: str = Field(description="Pedagogical explanation of why this answer is correct")


class QuizPublic(BaseModel):
    """Public quiz model sent to the client."""
    id: str = Field(description="Quiz ID")
    lesson_id: str = Field(description="Associated lesson ID")
    title: str = Field(description="Quiz title")
    questions: List[QuizQuestionPublic] = Field(description="Questions list")
    passing_score_percent: int = Field(default=70, description="Minimum score to pass")


class QuizAnswerSubmission(BaseModel):
    """User response for a single question."""
    question_id: str
    selected_option_id: str


class QuizSubmissionRequest(BaseModel):
    """Payload when submitting a quiz for grading."""
    answers: List[QuizAnswerSubmission]


class QuestionFeedback(BaseModel):
    """Detailed grading result for an individual question."""
    question_id: str
    selected_option_id: str
    correct_option_id: str
    is_correct: bool
    explanation: str


class QuizSubmissionResult(BaseModel):
    """Deterministic grading result returned by the backend."""
    quiz_id: str
    total_questions: int
    correct_count: int
    score_percentage: float
    passed: bool
    feedback: List[QuestionFeedback]
    graded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =====================================================================
# Lesson Models
# =====================================================================

class LessonExample(BaseModel):
    """Practical example scenario within a lesson."""
    title: str
    context: str
    scenario: str
    takeaway: str
    disclaimer: str = Field(
        default="Educational example only. Not a live trading recommendation or guarantee of price movement."
    )


class LessonSummary(BaseModel):
    """Brief metadata for lessons when listed in a course syllabus."""
    id: str
    course_id: str
    title: str
    order: int
    duration: str
    category: LearningCategory
    difficulty: DifficultyLevel


class LessonDetail(BaseModel):
    """Comprehensive lesson document for the Lesson Viewer."""
    id: str
    course_id: str
    title: str
    order: int
    duration: str
    category: LearningCategory
    difficulty: DifficultyLevel
    learning_objective: str
    explanation: str
    key_concepts: List[str]
    examples: List[LessonExample]
    important_notes: List[str]
    common_mistakes: List[str]
    limitations: List[str]
    illustration_key: Optional[str] = None
    quiz: Optional[QuizPublic] = None
    prev_lesson_id: Optional[str] = None
    next_lesson_id: Optional[str] = None


# =====================================================================
# Course Models
# =====================================================================

class CourseSummary(BaseModel):
    """Card overview of a course."""
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    category: LearningCategory
    estimated_duration: str
    lesson_count: int
    learning_objectives: List[str]
    prerequisites: List[str] = Field(default_factory=list)


class CourseDetail(CourseSummary):
    """Complete course with lesson syllabus."""
    lessons: List[LessonSummary] = Field(default_factory=list)


# =====================================================================
# Progress & Bookmarks Models
# =====================================================================

class ProgressUpdateRequest(BaseModel):
    """Request payload to update user progress."""
    lesson_id: str
    completed: bool = True
    course_id: Optional[str] = None


class BookmarkRequest(BaseModel):
    """Request payload to bookmark a lesson."""
    lesson_id: str
    note: Optional[str] = None


class UserLearningProgress(BaseModel):
    """User learning progress snapshot."""
    user_id: str = "guest_user"
    completed_lesson_ids: List[str] = Field(default_factory=list)
    in_progress_course_ids: List[str] = Field(default_factory=list)
    completed_course_ids: List[str] = Field(default_factory=list)
    quiz_scores: Dict[str, float] = Field(default_factory=dict, description="quiz_id -> best score percentage")
    bookmarked_lesson_ids: List[str] = Field(default_factory=list)
    last_accessed_lesson_id: Optional[str] = None
    last_accessed_course_id: Optional[str] = None
    is_local_session: bool = Field(default=True, description="Indicates progress is stored locally/in-memory until Phase 10 MongoDB")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =====================================================================
# Search & Category Models
# =====================================================================

class CategoryInfo(BaseModel):
    """Category metadata and aggregate counts."""
    name: LearningCategory
    description: str
    course_count: int
    lesson_count: int
    primary_level: DifficultyLevel


class LearningSearchResponse(BaseModel):
    """Search results across courses and lessons."""
    query: str
    total_results: int
    courses: List[CourseSummary]
    lessons: List[LessonSummary]
