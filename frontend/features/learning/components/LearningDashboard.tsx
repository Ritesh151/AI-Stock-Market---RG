"use client";

import React, { useState } from "react";
import {
  GraduationCap,
  BookOpen,
  Award,
  Bookmark,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Layers,
  ShieldCheck,
} from "lucide-react";
import {
  CategoryInfo,
  CourseSummary,
  DifficultyLevel,
  LearningCategory,
  UserLearningProgress,
} from "../types/learning";
import { CourseGrid } from "./CourseGrid";
import { LearningSearch } from "./LearningSearch";

interface LearningDashboardProps {
  courses: CourseSummary[];
  categories: CategoryInfo[];
  progress: UserLearningProgress;
  onSelectCourse: (courseId: string) => void;
  onSelectLesson: (lessonId: string, courseId: string) => void;
  className?: string;
}

export const LearningDashboard: React.FC<LearningDashboardProps> = ({
  courses,
  categories,
  progress,
  onSelectCourse,
  onSelectLesson,
  className = "",
}) => {
  const [selectedDifficulty, setSelectedDifficulty] = useState<DifficultyLevel | "ALL">("ALL");
  const [selectedCategory, setSelectedCategory] = useState<LearningCategory | "ALL">("ALL");

  // Filter courses based on selections
  const filteredCourses = courses.filter((c) => {
    if (selectedDifficulty !== "ALL" && c.difficulty !== selectedDifficulty) {
      return false;
    }
    if (selectedCategory !== "ALL" && c.category !== selectedCategory) {
      return false;
    }
    return true;
  });

  const completedCount = progress.completed_lesson_ids?.length || 0;
  const inProgressCount = progress.in_progress_course_ids?.length || 0;
  const bookmarkedCount = progress.bookmarked_lesson_ids?.length || 0;
  const totalLessonsInCurriculum = courses.reduce(
    (acc, c) => acc + c.lesson_count,
    0
  );
  const overallPercentage =
    totalLessonsInCurriculum > 0
      ? Math.round((completedCount / totalLessonsInCurriculum) * 100)
      : 0;

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Welcome Banner & Stats Overview */}
      <section className="relative overflow-hidden rounded-3xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 md:p-8 shadow-xs">
        <div className="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#176B45]/20 bg-[#176B45]/5 px-3 py-1 text-xs font-semibold text-[#176B45]">
              <GraduationCap className="h-4 w-4" />
              <span>RG AI Financial Education Platform</span>
            </div>
            <h1 className="mt-3 font-serif text-2xl font-bold tracking-tight text-[#20251F] sm:text-3xl">
              Indian Stock Market Academy
            </h1>
            <p className="mt-2 text-xs leading-relaxed text-[#777D76] sm:text-sm">
              Structured curriculum covering market fundamentals, 13 candlestick patterns, technical indicators, risk management formulas, and disciplined trading psychology.
            </p>
          </div>

          {/* Progress Snapshot Card */}
          <div className="flex shrink-0 flex-wrap items-center gap-4 rounded-2xl border border-[#E8EAE4] bg-[#F8F8F5] p-4 sm:p-5">
            <div>
              <div className="text-[11px] font-bold uppercase tracking-wider text-[#777D76]">
                Overall Completion
              </div>
              <div className="mt-1 font-mono text-2xl font-bold text-[#176B45]">
                {overallPercentage}%
              </div>
              <div className="text-[11px] text-[#777D76]">
                {completedCount} of {totalLessonsInCurriculum} lessons completed
              </div>
            </div>

            <div className="h-10 w-px bg-[#E8EAE4] hidden sm:block" />

            <div className="space-y-1.5 text-xs">
              <div className="flex items-center gap-2 text-[#777D76]">
                <BookOpen className="h-3.5 w-3.5 text-[#176B45]" />
                <span>
                  <strong className="text-[#20251F]">{inProgressCount}</strong> courses in progress
                </span>
              </div>
              <div className="flex items-center gap-2 text-[#777D76]">
                <Bookmark className="h-3.5 w-3.5 text-[#176B45]" />
                <span>
                  <strong className="text-[#20251F]">{bookmarkedCount}</strong> saved lessons
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Persistence Notice */}
        <div className="mt-6 flex items-center gap-2 rounded-xl bg-[#F1F2ED]/70 px-3 py-2 text-[11px] text-[#777D76]">
          <ShieldCheck className="h-3.5 w-3.5 text-[#176B45] shrink-0" />
          <span>
            Progress is currently saved locally to this session/device. Permanent cloud account persistence will be enabled in Phase 10 (MongoDB).
          </span>
        </div>
      </section>

      {/* Recommended Next Lesson / Resume Shelf */}
      {progress.last_accessed_lesson_id && (
        <section className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-[#176B45]/20 bg-[#176B45]/5 p-4 sm:p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#176B45] text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#176B45]">
                Resume Learning
              </span>
              <h4 className="text-sm font-bold text-[#20251F]">
                Continue from your last accessed lesson
              </h4>
            </div>
          </div>
          <button
            type="button"
            onClick={() =>
              onSelectLesson(
                progress.last_accessed_lesson_id!,
                progress.last_accessed_course_id || courses[0].id
              )
            }
            className="inline-flex items-center gap-1.5 rounded-xl bg-[#176B45] px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-[#125837]"
          >
            <span>Resume Lesson</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </section>
      )}

      {/* Search & Multi-Level Filter Toolbar */}
      <section className="space-y-4">
        <LearningSearch
          onSelectCourse={onSelectCourse}
          onSelectLesson={onSelectLesson}
          selectedDifficulty={selectedDifficulty}
          onDifficultyChange={setSelectedDifficulty}
        />

        {/* 14 Categories Horizontal Filter Shelf */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          <button
            type="button"
            onClick={() => setSelectedCategory("ALL")}
            className={`shrink-0 rounded-xl px-3 py-1.5 text-xs font-semibold transition-all ${
              selectedCategory === "ALL"
                ? "bg-[#20251F] text-white shadow-xs"
                : "border border-[#E8EAE4] bg-[#FFFFFF] text-[#777D76] hover:bg-[#F8F8F5] hover:text-[#20251F]"
            }`}
          >
            All Categories ({categories.length})
          </button>
          {categories.map((cat) => (
            <button
              key={cat.name}
              type="button"
              onClick={() => setSelectedCategory(cat.name)}
              className={`shrink-0 rounded-xl px-3 py-1.5 text-xs font-semibold transition-all ${
                selectedCategory === cat.name
                  ? "bg-[#176B45] text-white shadow-xs"
                  : "border border-[#E8EAE4] bg-[#FFFFFF] text-[#777D76] hover:bg-[#F8F8F5] hover:text-[#20251F]"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </section>

      {/* Courses Grid Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif text-lg font-bold text-[#20251F]">
              Available Courses ({filteredCourses.length})
            </h2>
            <p className="text-xs text-[#777D76]">
              Structured progressive modules with practical scenarios and knowledge checks.
            </p>
          </div>
        </div>

        <CourseGrid
          courses={filteredCourses}
          progress={progress}
          onSelectCourse={onSelectCourse}
        />
      </section>

      {/* Quick Access Educational Highlights Grid */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div
          onClick={() => onSelectCourse("course-candlestick-mastery")}
          className="group flex flex-col justify-between rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-5 shadow-xs transition-all hover:-translate-y-0.5 hover:border-[#176B45]/40 cursor-pointer"
        >
          <div>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#16834A]/10 text-[#16834A]">
              <Layers className="h-4 w-4" />
            </div>
            <h4 className="mt-3 font-serif text-sm font-bold text-[#20251F] group-hover:text-[#176B45]">
              Candlestick Pattern Library
            </h4>
            <p className="mt-1 text-xs text-[#777D76]">
              Master 13 core reversal and continuation patterns with SVG anatomical diagrams.
            </p>
          </div>
          <span className="mt-4 text-xs font-semibold text-[#176B45]">
            Explore 13 Patterns &rarr;
          </span>
        </div>

        <div
          onClick={() => onSelectCourse("course-technical-indicators")}
          className="group flex flex-col justify-between rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-5 shadow-xs transition-all hover:-translate-y-0.5 hover:border-[#176B45]/40 cursor-pointer"
        >
          <div>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#176B45]/10 text-[#176B45]">
              <TrendingUp className="h-4 w-4" />
            </div>
            <h4 className="mt-3 font-serif text-sm font-bold text-[#20251F] group-hover:text-[#176B45]">
              Technical Indicator Suite
            </h4>
            <p className="mt-1 text-xs text-[#777D76]">
              RSI, MACD, Moving Average Golden Crosses, and Volume confirmation models.
            </p>
          </div>
          <span className="mt-4 text-xs font-semibold text-[#176B45]">
            Study Indicators &rarr;
          </span>
        </div>

        <div
          onClick={() => onSelectCourse("course-risk-management")}
          className="group flex flex-col justify-between rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-5 shadow-xs transition-all hover:-translate-y-0.5 hover:border-[#176B45]/40 cursor-pointer"
        >
          <div>
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#D64A4A]/10 text-[#D64A4A]">
              <Award className="h-4 w-4" />
            </div>
            <h4 className="mt-3 font-serif text-sm font-bold text-[#20251F] group-hover:text-[#176B45]">
              1% Risk Rule & Position Sizing
            </h4>
            <p className="mt-1 text-xs text-[#777D76]">
              Mathematical capital preservation formulas and risk-to-reward profiling in INR.
            </p>
          </div>
          <span className="mt-4 text-xs font-semibold text-[#176B45]">
            Calculate Position Size &rarr;
          </span>
        </div>
      </section>
    </div>
  );
};
