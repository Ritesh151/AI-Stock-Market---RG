/**
 * Learning API Client for RG AI Education Platform.
 * Communicates with FastAPI backend (/api/v1/learning) with local storage sync.
 */

import {
  CategoryInfo,
  CourseDetail,
  CourseSummary,
  DifficultyLevel,
  LearningCategory,
  LearningSearchResponse,
  LessonDetail,
  QuizAnswerSubmission,
  QuizSubmissionResult,
  UserLearningProgress,
} from "../types/learning";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const LOCAL_STORAGE_PROGRESS_KEY = "rg_ai_learning_progress";

export interface ListCoursesParams {
  category?: LearningCategory;
  difficulty?: DifficultyLevel;
  limit?: number;
  skip?: number;
}

/**
 * Fetch courses list.
 */
export async function fetchCourses(
  params?: ListCoursesParams
): Promise<CourseSummary[]> {
  const query = new URLSearchParams();
  if (params?.category) query.set("category", params.category);
  if (params?.difficulty) query.set("difficulty", params.difficulty);
  if (params?.limit) query.set("limit", String(params.limit));
  if (params?.skip) query.set("skip", String(params.skip));

  const url = `${API_BASE_URL}/api/v1/learning/courses?${query.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch courses: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch course details with lesson syllabus.
 */
export async function fetchCourseDetail(courseId: string): Promise<CourseDetail> {
  const url = `${API_BASE_URL}/api/v1/learning/courses/${encodeURIComponent(courseId)}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch course detail: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch lesson content, examples, notes, and quiz.
 */
export async function fetchLessonDetail(lessonId: string): Promise<LessonDetail> {
  const url = `${API_BASE_URL}/api/v1/learning/lessons/${encodeURIComponent(lessonId)}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch lesson detail: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Fetch all 14 categories.
 */
export async function fetchCategories(): Promise<CategoryInfo[]> {
  const url = `${API_BASE_URL}/api/v1/learning/categories`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch categories: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Search courses and lessons.
 */
export async function searchLearningContent(
  query: string,
  limit: number = 20
): Promise<LearningSearchResponse> {
  const url = `${API_BASE_URL}/api/v1/learning/search?q=${encodeURIComponent(query)}&limit=${limit}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to search content: ${res.statusText}`);
  }
  return res.json();
}

/**
 * Read local fallback progress.
 */
function getLocalStoredProgress(): UserLearningProgress {
  if (typeof window === "undefined") {
    return {
      user_id: "guest_user",
      completed_lesson_ids: [],
      in_progress_course_ids: [],
      completed_course_ids: [],
      quiz_scores: {},
      bookmarked_lesson_ids: [],
      is_local_session: true,
      updated_at: new Date().toISOString(),
    };
  }
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_PROGRESS_KEY);
    if (raw) return JSON.parse(raw);
  } catch (err) {
    console.warn("Could not read local progress", err);
  }
  return {
    user_id: "guest_user",
    completed_lesson_ids: [],
    in_progress_course_ids: [],
    completed_course_ids: [],
    quiz_scores: {},
    bookmarked_lesson_ids: [],
    is_local_session: true,
    updated_at: new Date().toISOString(),
  };
}

/**
 * Save to local storage.
 */
function saveLocalStoredProgress(progress: UserLearningProgress): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(LOCAL_STORAGE_PROGRESS_KEY, JSON.stringify(progress));
  } catch (err) {
    console.warn("Could not save local progress", err);
  }
}

/**
 * Fetch user progress from backend, with local cache sync.
 */
export async function fetchUserProgress(
  userId: string = "guest_user"
): Promise<UserLearningProgress> {
  try {
    const url = `${API_BASE_URL}/api/v1/learning/progress?user_id=${encodeURIComponent(userId)}`;
    const res = await fetch(url);
    if (res.ok) {
      const data: UserLearningProgress = await res.json();
      saveLocalStoredProgress(data);
      return data;
    }
  } catch (err) {
    console.warn("Network error fetching progress, falling back to local store", err);
  }
  return getLocalStoredProgress();
}

/**
 * Record lesson completion / last accessed.
 */
export async function recordLessonProgress(
  lessonId: string,
  completed: boolean = true,
  courseId?: string,
  userId: string = "guest_user"
): Promise<UserLearningProgress> {
  // Update local store immediately for instant snappy UI
  const local = getLocalStoredProgress();
  local.last_accessed_lesson_id = lessonId;
  if (courseId) {
    local.last_accessed_course_id = courseId;
    if (!local.in_progress_course_ids.includes(courseId)) {
      local.in_progress_course_ids.push(courseId);
    }
  }
  if (completed && !local.completed_lesson_ids.includes(lessonId)) {
    local.completed_lesson_ids.push(lessonId);
  }
  local.updated_at = new Date().toISOString();
  saveLocalStoredProgress(local);

  try {
    const url = `${API_BASE_URL}/api/v1/learning/progress?user_id=${encodeURIComponent(userId)}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        lesson_id: lessonId,
        completed,
        course_id: courseId,
      }),
    });
    if (res.ok) {
      const backendProgress: UserLearningProgress = await res.json();
      saveLocalStoredProgress(backendProgress);
      return backendProgress;
    }
  } catch (err) {
    console.warn("Failed to sync progress to backend", err);
  }
  return local;
}

/**
 * Add lesson bookmark.
 */
export async function addLessonBookmark(
  lessonId: string,
  note?: string,
  userId: string = "guest_user"
): Promise<UserLearningProgress> {
  const local = getLocalStoredProgress();
  if (!local.bookmarked_lesson_ids.includes(lessonId)) {
    local.bookmarked_lesson_ids.push(lessonId);
  }
  local.updated_at = new Date().toISOString();
  saveLocalStoredProgress(local);

  try {
    const url = `${API_BASE_URL}/api/v1/learning/bookmarks?user_id=${encodeURIComponent(userId)}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lesson_id: lessonId, note }),
    });
    if (res.ok) {
      const backendProgress: UserLearningProgress = await res.json();
      saveLocalStoredProgress(backendProgress);
      return backendProgress;
    }
  } catch (err) {
    console.warn("Failed to sync bookmark to backend", err);
  }
  return local;
}

/**
 * Remove lesson bookmark.
 */
export async function removeLessonBookmark(
  lessonId: string,
  userId: string = "guest_user"
): Promise<UserLearningProgress> {
  const local = getLocalStoredProgress();
  local.bookmarked_lesson_ids = local.bookmarked_lesson_ids.filter(
    (id) => id !== lessonId
  );
  local.updated_at = new Date().toISOString();
  saveLocalStoredProgress(local);

  try {
    const url = `${API_BASE_URL}/api/v1/learning/bookmarks/${encodeURIComponent(lessonId)}?user_id=${encodeURIComponent(userId)}`;
    const res = await fetch(url, { method: "DELETE" });
    if (res.ok) {
      const backendProgress: UserLearningProgress = await res.json();
      saveLocalStoredProgress(backendProgress);
      return backendProgress;
    }
  } catch (err) {
    console.warn("Failed to sync bookmark delete to backend", err);
  }
  return local;
}

/**
 * Submit quiz for deterministic backend grading.
 */
export async function submitQuizAnswers(
  quizId: string,
  answers: QuizAnswerSubmission[],
  userId: string = "guest_user"
): Promise<QuizSubmissionResult> {
  const url = `${API_BASE_URL}/api/v1/learning/quizzes/${encodeURIComponent(quizId)}/submit?user_id=${encodeURIComponent(userId)}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
  if (!res.ok) {
    throw new Error(`Quiz grading failed: ${res.statusText}`);
  }
  const result: QuizSubmissionResult = await res.json();

  // Optimistically store in local progress
  const local = getLocalStoredProgress();
  const currentBest = local.quiz_scores[quizId] || 0;
  if (result.score_percentage > currentBest) {
    local.quiz_scores[quizId] = result.score_percentage;
    local.updated_at = new Date().toISOString();
    saveLocalStoredProgress(local);
  }

  return result;
}
