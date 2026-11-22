"""
Automated Pytest Suite for Phase 9: RG AI Learn Trading Platform.
Validates course catalog, syllabus retrieval, lesson content, all 14 categories,
search, deterministic quiz scoring, and user progress/bookmark workflows.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.schemas.learning import DifficultyLevel, LearningCategory

app = create_app()
client = TestClient(app)


def test_list_courses_all():
    """Verify listing all courses returns populated course summaries."""
    response = client.get("/api/v1/learning/courses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 6

    # Verify summary fields
    first = data[0]
    assert "id" in first
    assert "title" in first
    assert "difficulty" in first
    assert "category" in first
    assert "estimated_duration" in first
    assert "lesson_count" in first
    assert "learning_objectives" in first


def test_list_courses_filter_by_difficulty():
    """Verify filtering courses by difficulty level."""
    response = client.get("/api/v1/learning/courses?difficulty=BEGINNER")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all(c["difficulty"] == "BEGINNER" for c in courses)

    response_adv = client.get("/api/v1/learning/courses?difficulty=ADVANCED")
    assert response_adv.status_code == 200
    adv_courses = response_adv.json()
    assert len(adv_courses) > 0
    assert all(c["difficulty"] == "ADVANCED" for c in adv_courses)


def test_list_courses_filter_by_category():
    """Verify filtering courses by category."""
    response = client.get(
        f"/api/v1/learning/courses?category={LearningCategory.CANDLESTICK_PATTERNS.value}"
    )
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all(c["category"] == LearningCategory.CANDLESTICK_PATTERNS.value for c in courses)


def test_get_course_detail_success():
    """Verify retrieving full course detail including syllabus."""
    response = client.get("/api/v1/learning/courses/course-candlestick-mastery")
    assert response.status_code == 200
    course = response.json()
    assert course["id"] == "course-candlestick-mastery"
    assert "lessons" in course
    assert len(course["lessons"]) == 5
    first_lesson = course["lessons"][0]
    assert first_lesson["id"] == "lesson-candle-anatomy-doji"
    assert first_lesson["order"] == 1


def test_get_course_detail_not_found():
    """Verify 404 response for nonexistent course."""
    response = client.get("/api/v1/learning/courses/nonexistent-course-id")
    assert response.status_code == 404
    data = response.json()
    err_msg = data.get("detail") or data.get("error", {}).get("message", "")
    assert "not found" in err_msg.lower()


def test_get_lesson_detail_success():
    """Verify retrieving comprehensive lesson content, examples, notes, and quiz."""
    response = client.get("/api/v1/learning/lessons/lesson-hammer-shooting-star")
    assert response.status_code == 200
    lesson = response.json()
    assert lesson["id"] == "lesson-hammer-shooting-star"
    assert lesson["title"] == "Hammer, Inverted Hammer, Shooting Star & Hanging Man"
    assert len(lesson["key_concepts"]) >= 3
    assert len(lesson["examples"]) >= 1
    assert "disclaimer" in lesson["examples"][0]
    assert len(lesson["important_notes"]) >= 1
    assert len(lesson["limitations"]) >= 1
    assert lesson["prev_lesson_id"] is not None
    assert lesson["next_lesson_id"] is not None

    # Verify inline quiz is included and does NOT leak correct_option_id
    assert lesson["quiz"] is not None
    quiz = lesson["quiz"]
    assert len(quiz["questions"]) >= 2
    for q in quiz["questions"]:
        assert "question" in q
        assert "options" in q
        assert "correct_option_id" not in q  # Must not leak answer keys!


def test_get_lesson_detail_not_found():
    """Verify 404 response for nonexistent lesson."""
    response = client.get("/api/v1/learning/lessons/nonexistent-lesson-id")
    assert response.status_code == 404


def test_list_all_14_categories():
    """Verify that all 14 required learning categories exist."""
    response = client.get("/api/v1/learning/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 14

    category_names = [c["name"] for c in categories]
    for expected_cat in LearningCategory:
        assert expected_cat.value in category_names


def test_search_content():
    """Verify searching across curriculum."""
    response = client.get("/api/v1/learning/search?q=candlestick")
    assert response.status_code == 200
    data = response.json()
    assert data["total_results"] > 0
    assert len(data["courses"]) > 0 or len(data["lessons"]) > 0

    # Search for specific term like RSI
    rsi_resp = client.get("/api/v1/learning/search?q=RSI")
    assert rsi_resp.status_code == 200
    rsi_data = rsi_resp.json()
    assert rsi_data["total_results"] > 0


def test_user_progress_tracking():
    """Verify getting and updating learning progress."""
    user_id = "test_user_progress_01"

    # Get initial empty progress
    initial_resp = client.get(f"/api/v1/learning/progress?user_id={user_id}")
    assert initial_resp.status_code == 200
    progress = initial_resp.json()
    assert progress["user_id"] == user_id
    assert len(progress["completed_lesson_ids"]) == 0
    assert progress["is_local_session"] is True

    # Mark lesson completed
    update_resp = client.post(
        f"/api/v1/learning/progress?user_id={user_id}",
        json={
            "lesson_id": "lesson-nse-bse-structure",
            "completed": True,
            "course_id": "course-market-basics",
        },
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert "lesson-nse-bse-structure" in updated["completed_lesson_ids"]
    assert updated["last_accessed_lesson_id"] == "lesson-nse-bse-structure"
    assert "course-market-basics" in updated["in_progress_course_ids"]


def test_bookmarks_lifecycle():
    """Verify adding and removing bookmarks."""
    user_id = "test_user_bookmarks_01"

    # Add bookmark
    add_resp = client.post(
        f"/api/v1/learning/bookmarks?user_id={user_id}",
        json={"lesson_id": "lesson-one-percent-rule", "note": "Crucial risk formula"},
    )
    assert add_resp.status_code == 200
    data = add_resp.json()
    assert "lesson-one-percent-rule" in data["bookmarked_lesson_ids"]

    # Remove bookmark
    del_resp = client.delete(
        f"/api/v1/learning/bookmarks/lesson-one-percent-rule?user_id={user_id}"
    )
    assert del_resp.status_code == 200
    del_data = del_resp.json()
    assert "lesson-one-percent-rule" not in del_data["bookmarked_lesson_ids"]


def test_deterministic_quiz_evaluation_perfect_score():
    """Verify backend accurately scores 100% on correct submissions with explanations."""
    user_id = "test_user_quiz_perfect"
    quiz_id = "quiz-lesson-order-types"

    answers = [
        {"question_id": "q-ord-1", "selected_option_id": "opt-b"},
        {"question_id": "q-ord-2", "selected_option_id": "opt-b"},
        {"question_id": "q-ord-3", "selected_option_id": "opt-b"},
    ]

    response = client.post(
        f"/api/v1/learning/quizzes/{quiz_id}/submit?user_id={user_id}",
        json={"answers": answers},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["quiz_id"] == quiz_id
    assert result["total_questions"] == 3
    assert result["correct_count"] == 3
    assert result["score_percentage"] == 100.0
    assert result["passed"] is True
    assert len(result["feedback"]) == 3
    for fb in result["feedback"]:
        assert fb["is_correct"] is True
        assert len(fb["explanation"]) > 10

    # Verify quiz score is stored in progress
    progress_resp = client.get(f"/api/v1/learning/progress?user_id={user_id}")
    prog = progress_resp.json()
    assert prog["quiz_scores"][quiz_id] == 100.0


def test_deterministic_quiz_evaluation_partial_and_fail():
    """Verify backend accurately evaluates incorrect answers and fails below passing score."""
    user_id = "test_user_quiz_fail"
    quiz_id = "quiz-lesson-order-types"

    # Only 1 correct out of 3 (33.3%)
    answers = [
        {"question_id": "q-ord-1", "selected_option_id": "opt-b"},  # Correct
        {"question_id": "q-ord-2", "selected_option_id": "opt-a"},  # Incorrect
        {"question_id": "q-ord-3", "selected_option_id": "opt-a"},  # Incorrect
    ]

    response = client.post(
        f"/api/v1/learning/quizzes/{quiz_id}/submit?user_id={user_id}",
        json={"answers": answers},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["correct_count"] == 1
    assert result["score_percentage"] == 33.3
    assert result["passed"] is False
    assert result["feedback"][0]["is_correct"] is True
    assert result["feedback"][1]["is_correct"] is False
    assert result["feedback"][2]["is_correct"] is False


def test_quiz_submit_not_found():
    """Verify 404 for submitting nonexistent quiz."""
    response = client.post(
        "/api/v1/learning/quizzes/nonexistent-quiz-id/submit",
        json={"answers": []},
    )
    assert response.status_code == 404
