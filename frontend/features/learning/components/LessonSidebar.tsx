"use client";

import React from "react";
import { CheckCircle2, Circle, Clock, ArrowLeft, BookOpen } from "lucide-react";
import { CourseDetail, UserLearningProgress } from "../types/learning";

interface LessonSidebarProps {
  course: CourseDetail;
  activeLessonId: string;
  progress?: UserLearningProgress;
  onSelectLesson: (lessonId: string) => void;
  onBackToDashboard: () => void;
  className?: string;
}

export const LessonSidebar: React.FC<LessonSidebarProps> = ({
  course,
  activeLessonId,
  progress,
  onSelectLesson,
  onBackToDashboard,
  className = "",
}) => {
  const completedIds = progress?.completed_lesson_ids || [];

  return (
    <aside
      className={`flex flex-col rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-4 shadow-xs ${className}`}
    >
      {/* Back to Courses Link */}
      <button
        type="button"
        onClick={onBackToDashboard}
        className="mb-4 inline-flex items-center gap-1.5 text-xs font-semibold text-[#777D76] transition-colors hover:text-[#20251F]"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        All Courses
      </button>

      {/* Course Title Header */}
      <div className="border-b border-[#E8EAE4] pb-4">
        <span className="rounded-md bg-[#F1F2ED] px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[#777D76]">
          {course.difficulty} &bull; {course.category}
        </span>
        <h2 className="mt-2 font-serif text-sm font-bold text-[#20251F] leading-snug">
          {course.title}
        </h2>
        <div className="mt-2 flex items-center gap-3 text-[11px] text-[#777D76]">
          <span className="flex items-center gap-1">
            <BookOpen className="h-3 w-3" />
            {course.lessons.length} lessons
          </span>
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {course.estimated_duration}
          </span>
        </div>
      </div>

      {/* Syllabus Navigation List */}
      <div className="mt-4 flex-1 space-y-1.5 overflow-y-auto pr-1">
        <span className="text-[10px] font-bold uppercase tracking-wider text-[#777D76]">
          Course Syllabus
        </span>
        {course.lessons.map((lesson, idx) => {
          const isActive = lesson.id === activeLessonId;
          const isCompleted = completedIds.includes(lesson.id);

          return (
            <button
              key={lesson.id}
              type="button"
              onClick={() => onSelectLesson(lesson.id)}
              className={`flex w-full items-start gap-2.5 rounded-xl p-2.5 text-left text-xs transition-all ${
                isActive
                  ? "border border-[#176B45] bg-[#176B45]/5 font-semibold text-[#176B45]"
                  : "border border-transparent text-[#20251F] hover:bg-[#F8F8F5]"
              }`}
            >
              <div className="mt-0.5 shrink-0">
                {isCompleted ? (
                  <CheckCircle2 className="h-4 w-4 text-[#16834A]" />
                ) : (
                  <Circle
                    className={`h-4 w-4 ${
                      isActive ? "text-[#176B45]" : "text-[#777D76]/50"
                    }`}
                  />
                )}
              </div>
              <div className="flex-1">
                <div className="line-clamp-2">
                  <span className="mr-1 text-[11px] text-[#777D76] font-mono">
                    {idx + 1}.
                  </span>
                  {lesson.title}
                </div>
                <div className="mt-1 flex items-center gap-1 text-[10px] text-[#777D76]">
                  <Clock className="h-2.5 w-2.5" />
                  {lesson.duration}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </aside>
  );
};
