"use client";

import React from "react";
import { Clock, BookOpen, CheckCircle2 } from "lucide-react";
import { CourseSummary, UserLearningProgress } from "../types/learning";
import { ProgressIndicator } from "./ProgressIndicator";

interface CourseCardProps {
  course: CourseSummary;
  progress?: UserLearningProgress;
  onSelect: (courseId: string) => void;
  className?: string;
}

export const CourseCard: React.FC<CourseCardProps> = ({
  course,
  progress,
  onSelect,
  className = "",
}) => {
  const isCompleted = progress?.completed_course_ids?.includes(course.id);
  const isInProgress = progress?.in_progress_course_ids?.includes(course.id);

  // Approximate completed count from completed lessons in progress
  const completedLessonsCount = isCompleted
    ? course.lesson_count
    : isInProgress
    ? Math.min(course.lesson_count - 1, 1)
    : 0;

  const difficultyBadgeStyle =
    course.difficulty === "BEGINNER"
      ? "bg-[#16834A]/10 text-[#16834A] border-[#16834A]/20"
      : course.difficulty === "INTERMEDIATE"
      ? "bg-[#176B45]/10 text-[#176B45] border-[#176B45]/20"
      : "bg-[#20251F]/10 text-[#20251F] border-[#20251F]/20";

  return (
    <div
      onClick={() => onSelect(course.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(course.id);
        }
      }}
      className={`group relative flex flex-col justify-between rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-5 shadow-xs transition-all duration-200 hover:-translate-y-1 hover:border-[#176B45]/30 hover:shadow-md cursor-pointer ${className}`}
    >
      <div>
        {/* Top Badges Row */}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span
            className={`rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${difficultyBadgeStyle}`}
          >
            {course.difficulty}
          </span>
          <span className="rounded-full bg-[#F1F2ED] px-2.5 py-0.5 text-[11px] font-medium text-[#777D76]">
            {course.category}
          </span>
        </div>

        {/* Title & Description */}
        <h3 className="mt-3 font-serif text-base font-bold text-[#20251F] group-hover:text-[#176B45] transition-colors">
          {course.title}
        </h3>
        <p className="mt-1.5 text-xs line-clamp-2 text-[#777D76] leading-relaxed">
          {course.description}
        </p>

        {/* Learning Objectives Preview */}
        {course.learning_objectives.length > 0 && (
          <div className="mt-3 space-y-1 border-t border-[#E8EAE4]/60 pt-3">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-[#777D76]">
              Key Objectives:
            </span>
            <ul className="space-y-1">
              {course.learning_objectives.slice(0, 2).map((obj, i) => (
                <li
                  key={i}
                  className="flex items-start gap-1.5 text-[11px] text-[#777D76]"
                >
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#176B45]" />
                  <span className="line-clamp-1">{obj}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Bottom Progress & Metadata */}
      <div className="mt-5 border-t border-[#E8EAE4] pt-4">
        {isInProgress || isCompleted ? (
          <div className="mb-3">
            <ProgressIndicator
              completed={completedLessonsCount}
              total={course.lesson_count}
              variant="linear"
            />
          </div>
        ) : null}

        <div className="flex items-center justify-between text-xs text-[#777D76]">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {course.estimated_duration}
            </span>
            <span className="flex items-center gap-1">
              <BookOpen className="h-3.5 w-3.5" />
              {course.lesson_count} lessons
            </span>
          </div>

          <div className="flex items-center gap-1 font-semibold text-[#176B45] group-hover:translate-x-1 transition-transform">
            {isCompleted ? (
              <span className="flex items-center gap-1 text-[#16834A]">
                <CheckCircle2 className="h-4 w-4" /> Completed
              </span>
            ) : isInProgress ? (
              <span>Resume &rarr;</span>
            ) : (
              <span>Start Course &rarr;</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
