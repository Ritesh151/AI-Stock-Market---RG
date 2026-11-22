"use client";

import React from "react";
import { CourseSummary, UserLearningProgress } from "../types/learning";
import { CourseCard } from "./CourseCard";

interface CourseGridProps {
  courses: CourseSummary[];
  progress?: UserLearningProgress;
  onSelectCourse: (courseId: string) => void;
  className?: string;
}

export const CourseGrid: React.FC<CourseGridProps> = ({
  courses,
  progress,
  onSelectCourse,
  className = "",
}) => {
  if (courses.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-[#E8EAE4] bg-[#FFFFFF] p-12 text-center">
        <p className="text-sm font-semibold text-[#20251F]">
          No courses found for this selection
        </p>
        <p className="mt-1 text-xs text-[#777D76]">
          Try clearing or adjusting your category or difficulty filters.
        </p>
      </div>
    );
  }

  return (
    <div
      className={`grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3 ${className}`}
    >
      {courses.map((course) => (
        <CourseCard
          key={course.id}
          course={course}
          progress={progress}
          onSelect={onSelectCourse}
        />
      ))}
    </div>
  );
};
