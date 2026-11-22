"use client";

import React, { useState } from "react";
import {
  Clock,
  CheckCircle2,
  ArrowLeft,
  ArrowRight,
  ShieldAlert,
  AlertTriangle,
  Lightbulb,
  BookOpen,
  Menu,
  X,
} from "lucide-react";
import { CourseDetail, LessonDetail, UserLearningProgress } from "../types/learning";
import { BookmarkButton } from "./BookmarkButton";
import { CandlestickIllustrator } from "./CandlestickIllustrator";
import { IndicatorIllustrator } from "./IndicatorIllustrator";
import { QuizComponent } from "./QuizComponent";
import { LessonSidebar } from "./LessonSidebar";
import { recordLessonProgress } from "../services/learningApi";

interface LessonViewerProps {
  course: CourseDetail;
  lesson: LessonDetail;
  progress?: UserLearningProgress;
  onNavigateLesson: (lessonId: string) => void;
  onBackToDashboard: () => void;
  onProgressUpdated?: (updated: UserLearningProgress) => void;
  className?: string;
}

export const LessonViewer: React.FC<LessonViewerProps> = ({
  course,
  lesson,
  progress,
  onNavigateLesson,
  onBackToDashboard,
  onProgressUpdated,
  className = "",
}) => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [markingComplete, setMarkingComplete] = useState(false);

  const isCompleted = progress?.completed_lesson_ids?.includes(lesson.id) || false;
  const isBookmarked = progress?.bookmarked_lesson_ids?.includes(lesson.id) || false;

  const handleToggleComplete = async () => {
    if (markingComplete) return;
    setMarkingComplete(true);
    try {
      const nextStatus = !isCompleted;
      const updated = await recordLessonProgress(
        lesson.id,
        nextStatus,
        course.id
      );
      if (onProgressUpdated) {
        onProgressUpdated(updated);
      }
    } catch (err) {
      console.warn("Failed to update lesson completion status", err);
    } finally {
      setMarkingComplete(false);
    }
  };

  const isCandlestickPattern =
    lesson.category === "Candlestick Patterns" ||
    (lesson.illustration_key && lesson.illustration_key.startsWith("pattern_"));

  return (
    <div className={`w-full ${className}`}>
      {/* Mobile Sidebar Toggle Bar */}
      <div className="mb-4 flex items-center justify-between lg:hidden">
        <button
          type="button"
          onClick={() => setMobileSidebarOpen(!mobileSidebarOpen)}
          className="inline-flex items-center gap-2 rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] px-3.5 py-2 text-xs font-semibold text-[#20251F]"
        >
          {mobileSidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
          <span>Course Navigation</span>
        </button>
        <button
          type="button"
          onClick={onBackToDashboard}
          className="text-xs font-semibold text-[#777D76] hover:text-[#20251F]"
        >
          &larr; Exit to Courses
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Sidebar (Desktop fixed, Mobile overlay drawer) */}
        <div
          className={`lg:col-span-4 ${
            mobileSidebarOpen
              ? "fixed inset-0 z-50 flex bg-black/40 p-4 lg:relative lg:bg-transparent lg:p-0"
              : "hidden lg:block"
          }`}
          onClick={(e) => {
            if (e.target === e.currentTarget) setMobileSidebarOpen(false);
          }}
        >
          <div className="h-full w-full max-w-sm lg:sticky lg:top-20">
            <LessonSidebar
              course={course}
              activeLessonId={lesson.id}
              progress={progress}
              onSelectLesson={(lid) => {
                onNavigateLesson(lid);
                setMobileSidebarOpen(false);
              }}
              onBackToDashboard={onBackToDashboard}
            />
          </div>
        </div>

        {/* Main Content Area */}
        <main className="lg:col-span-8 space-y-6">
          {/* Header Card */}
          <div className="rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-md bg-[#F1F2ED] px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider text-[#777D76]">
                  Lesson {lesson.order} of {course.lessons.length}
                </span>
                <span className="flex items-center gap-1 text-xs text-[#777D76]">
                  <Clock className="h-3.5 w-3.5" />
                  {lesson.duration}
                </span>
              </div>
              <BookmarkButton
                lessonId={lesson.id}
                initialBookmarked={isBookmarked}
              />
            </div>

            <h1 className="mt-3 font-serif text-2xl font-bold text-[#20251F]">
              {lesson.title}
            </h1>

            {/* Learning Objective Callout */}
            <div className="mt-4 flex items-start gap-3 rounded-xl border border-[#176B45]/20 bg-[#176B45]/5 p-3.5 text-xs">
              <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-[#176B45]" />
              <div>
                <span className="font-bold text-[#176B45]">Learning Objective: </span>
                <span className="text-[#20251F]">{lesson.learning_objective}</span>
              </div>
            </div>
          </div>

          {/* Educational Visual Illustration */}
          {lesson.illustration_key && (
            <div>
              {isCandlestickPattern ? (
                <CandlestickIllustrator patternKey={lesson.illustration_key} />
              ) : (
                <IndicatorIllustrator illustrationKey={lesson.illustration_key} />
              )}
            </div>
          )}

          {/* Detailed Explanation */}
          <article className="rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs">
            <h2 className="mb-3 font-serif text-lg font-bold text-[#20251F]">
              Detailed Explanation
            </h2>
            <p className="text-sm leading-relaxed text-[#20251F]/90">
              {lesson.explanation}
            </p>

            {/* Key Concepts List */}
            {lesson.key_concepts.length > 0 && (
              <div className="mt-6 border-t border-[#E8EAE4] pt-5">
                <h3 className="mb-3 text-xs font-bold uppercase tracking-wider text-[#777D76]">
                  Core Concepts & Market Mechanics
                </h3>
                <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  {lesson.key_concepts.map((concept, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2.5 rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3 text-xs"
                    >
                      <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#176B45]" />
                      <span className="text-[#20251F] font-medium leading-snug">
                        {concept}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </article>

          {/* Practical Examples */}
          {lesson.examples.length > 0 && (
            <div className="space-y-4">
              {lesson.examples.map((example, i) => (
                <div
                  key={i}
                  className="rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs"
                >
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#176B45]">
                    <BookOpen className="h-4 w-4" />
                    Practical Market Scenario: {example.title}
                  </div>
                  <div className="mt-1 text-xs text-[#777D76]">
                    <span className="font-semibold text-[#20251F]">Context: </span>
                    {example.context}
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-[#20251F]">
                    {example.scenario}
                  </p>
                  <div className="mt-3 rounded-lg bg-[#F8F8F5] p-3 text-xs font-medium text-[#176B45]">
                    Key Takeaway: {example.takeaway}
                  </div>
                  <div className="mt-2 text-[10px] text-[#777D76] italic">
                    {example.disclaimer}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pitfalls & Limitations */}
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            {lesson.common_mistakes.length > 0 && (
              <div className="rounded-2xl border border-[#D64A4A]/20 bg-[#FFFFFF] p-5 shadow-xs">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#D64A4A]">
                  <AlertTriangle className="h-4 w-4" />
                  Common Traps to Avoid
                </div>
                <ul className="mt-3 space-y-2">
                  {lesson.common_mistakes.map((mistake, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-xs text-[#777D76] leading-snug"
                    >
                      <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#D64A4A]" />
                      <span>{mistake}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {lesson.limitations.length > 0 && (
              <div className="rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-5 shadow-xs">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#777D76]">
                  <ShieldAlert className="h-4 w-4 text-[#176B45]" />
                  Technical Limitations
                </div>
                <ul className="mt-3 space-y-2">
                  {lesson.limitations.map((lim, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-xs text-[#777D76] leading-snug"
                    >
                      <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#777D76]" />
                      <span>{lim}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Inline Knowledge Check Quiz */}
          {lesson.quiz && (
            <div className="mt-6">
              <QuizComponent
                quiz={lesson.quiz}
                onQuizCompleted={(score) => {
                  if (score >= lesson.quiz!.passing_score_percent) {
                    recordLessonProgress(lesson.id, true, course.id);
                  }
                }}
              />
            </div>
          )}

          {/* Bottom Navigation Toolbar */}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-xs">
            <div>
              {lesson.prev_lesson_id ? (
                <button
                  type="button"
                  onClick={() => onNavigateLesson(lesson.prev_lesson_id!)}
                  className="inline-flex items-center gap-2 rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] px-4 py-2.5 text-xs font-semibold text-[#20251F] hover:bg-[#F8F8F5]"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  Previous Lesson
                </button>
              ) : (
                <span />
              )}
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleToggleComplete}
                disabled={markingComplete}
                className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-xs font-semibold transition-all ${
                  isCompleted
                    ? "border-[#16834A] bg-[#16834A]/10 text-[#16834A]"
                    : "border-[#E8EAE4] bg-[#FFFFFF] text-[#20251F] hover:border-[#176B45]/40"
                }`}
              >
                <CheckCircle2 className="h-4 w-4" />
                <span>{isCompleted ? "Completed" : "Mark as Completed"}</span>
              </button>

              {lesson.next_lesson_id ? (
                <button
                  type="button"
                  onClick={() => onNavigateLesson(lesson.next_lesson_id!)}
                  className="inline-flex items-center gap-2 rounded-xl bg-[#176B45] px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-[#125837]"
                >
                  <span>Next Lesson</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={onBackToDashboard}
                  className="inline-flex items-center gap-2 rounded-xl bg-[#176B45] px-4 py-2.5 text-xs font-semibold text-white shadow-xs hover:bg-[#125837]"
                >
                  <span>Finish Course</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
