/**
 * TypeScript Type Definitions for RG AI Learn Trading Education Platform.
 */

export type DifficultyLevel = "BEGINNER" | "INTERMEDIATE" | "ADVANCED";

export type LearningCategory =
  | "Stock Market Basics"
  | "Candlestick Patterns"
  | "Technical Analysis"
  | "Fundamental Analysis"
  | "Support and Resistance"
  | "RSI Indicator"
  | "MACD Indicator"
  | "Moving Averages"
  | "Volume Analysis"
  | "Risk Management"
  | "Trading Psychology"
  | "Swing Trading"
  | "Long-Term Investing"
  | "Portfolio Management";

export type QuestionType =
  | "MULTIPLE_CHOICE"
  | "TRUE_FALSE"
  | "CANDLESTICK_IDENTIFY"
  | "CONCEPT_IDENTIFY"
  | "SCENARIO_BASED";

export interface QuizOption {
  id: string;
  text: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  question_type: QuestionType;
  options: QuizOption[];
  scenario_context?: string;
  illustration_key?: string;
}

export interface QuizPublic {
  id: string;
  lesson_id: string;
  title: string;
  questions: QuizQuestion[];
  passing_score_percent: number;
}

export interface QuizAnswerSubmission {
  question_id: string;
  selected_option_id: string;
}

export interface QuestionFeedback {
  question_id: string;
  selected_option_id: string;
  correct_option_id: string;
  is_correct: boolean;
  explanation: string;
}

export interface QuizSubmissionResult {
  quiz_id: string;
  total_questions: number;
  correct_count: number;
  score_percentage: number;
  passed: boolean;
  feedback: QuestionFeedback[];
  graded_at: string;
}

export interface LessonExample {
  title: string;
  context: string;
  scenario: string;
  takeaway: string;
  disclaimer: string;
}

export interface LessonSummary {
  id: string;
  course_id: string;
  title: string;
  order: number;
  duration: string;
  category: LearningCategory;
  difficulty: DifficultyLevel;
}

export interface LessonDetail {
  id: string;
  course_id: string;
  title: string;
  order: number;
  duration: string;
  category: LearningCategory;
  difficulty: DifficultyLevel;
  learning_objective: string;
  explanation: string;
  key_concepts: string[];
  examples: LessonExample[];
  important_notes: string[];
  common_mistakes: string[];
  limitations: string[];
  illustration_key?: string;
  quiz?: QuizPublic;
  prev_lesson_id?: string;
  next_lesson_id?: string;
}

export interface CourseSummary {
  id: string;
  title: string;
  description: string;
  difficulty: DifficultyLevel;
  category: LearningCategory;
  estimated_duration: string;
  lesson_count: number;
  learning_objectives: string[];
  prerequisites: string[];
}

export interface CourseDetail extends CourseSummary {
  lessons: LessonSummary[];
}

export interface UserLearningProgress {
  user_id: string;
  completed_lesson_ids: string[];
  in_progress_course_ids: string[];
  completed_course_ids: string[];
  quiz_scores: Record<string, number>;
  bookmarked_lesson_ids: string[];
  last_accessed_lesson_id?: string;
  last_accessed_course_id?: string;
  is_local_session: boolean;
  updated_at: string;
}

export interface CategoryInfo {
  name: LearningCategory;
  description: string;
  course_count: number;
  lesson_count: number;
  primary_level: DifficultyLevel;
}

export interface LearningSearchResponse {
  query: string;
  total_results: number;
  courses: CourseSummary[];
  lessons: LessonSummary[];
}
