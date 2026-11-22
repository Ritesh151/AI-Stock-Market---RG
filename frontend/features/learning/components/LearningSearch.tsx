"use client";

import React, { useState, useEffect } from "react";
import { Search, X, Filter, Loader2, BookOpen } from "lucide-react";
import {
  DifficultyLevel,
  LearningSearchResponse,
} from "../types/learning";
import { searchLearningContent } from "../services/learningApi";

interface LearningSearchProps {
  onSelectCourse?: (courseId: string) => void;
  onSelectLesson?: (lessonId: string, courseId: string) => void;
  selectedDifficulty?: DifficultyLevel | "ALL";
  onDifficultyChange?: (difficulty: DifficultyLevel | "ALL") => void;
  className?: string;
}

export const LearningSearch: React.FC<LearningSearchProps> = ({
  onSelectCourse,
  onSelectLesson,
  selectedDifficulty = "ALL",
  onDifficultyChange,
  className = "",
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<LearningSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    if (!query.trim()) return;

    let ignore = false;
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await searchLearningContent(query.trim(), 10);
        if (!ignore) {
          setResults(data);
          setIsOpen(true);
        }
      } catch (err) {
        console.warn("Search failed", err);
      } finally {
        if (!ignore) setLoading(false);
      }
    }, 250);

    return () => {
      ignore = true;
      clearTimeout(timer);
    };
  }, [query]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    if (!val.trim()) {
      setResults(null);
      setIsOpen(false);
    }
  };

  const clearSearch = () => {
    setQuery("");
    setResults(null);
    setIsOpen(false);
  };

  return (
    <div className={`relative w-full ${className}`}>
      {/* Search Input Bar */}
      <div className="relative flex items-center">
        <Search className="pointer-events-none absolute left-3.5 h-4 w-4 text-[#777D76]" />
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          placeholder="Search lessons, candlestick patterns, RSI, support/resistance, risk..."
          className="w-full rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] py-2.5 pr-10 pl-10 text-xs text-[#20251F] placeholder-[#777D76] transition-all focus:border-[#176B45] focus:ring-1 focus:ring-[#176B45] focus:outline-hidden"
        />
        {loading ? (
          <Loader2 className="absolute right-3.5 h-4 w-4 animate-spin text-[#777D76]" />
        ) : query ? (
          <button
            type="button"
            onClick={clearSearch}
            className="absolute right-3 rounded p-0.5 text-[#777D76] hover:text-[#20251F]"
          >
            <X className="h-4 w-4" />
          </button>
        ) : null}
      </div>

      {/* Filter Chips Bar */}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5 text-[11px] font-medium text-[#777D76]">
          <Filter className="h-3 w-3" />
          Level:
        </div>
        {(["ALL", "BEGINNER", "INTERMEDIATE", "ADVANCED"] as const).map(
          (level) => (
            <button
              key={level}
              type="button"
              onClick={() => onDifficultyChange && onDifficultyChange(level)}
              className={`rounded-lg px-2.5 py-1 text-[11px] font-medium transition-all ${
                selectedDifficulty === level
                  ? "bg-[#176B45] text-white shadow-xs"
                  : "border border-[#E8EAE4] bg-[#FFFFFF] text-[#777D76] hover:bg-[#F8F8F5] hover:text-[#20251F]"
              }`}
            >
              {level === "ALL" ? "All Levels" : level}
            </button>
          )
        )}
      </div>

      {/* Instant Search Dropdown Popover */}
      {isOpen && results && (
        <div className="absolute z-50 mt-2 max-h-96 w-full overflow-y-auto rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] p-2 shadow-lg">
          {results.total_results === 0 ? (
            <div className="py-6 text-center text-xs text-[#777D76]">
              No courses or lessons found matching &ldquo;{query}&rdquo;.
            </div>
          ) : (
            <div className="space-y-3">
              {results.courses.length > 0 && (
                <div>
                  <span className="px-2 text-[10px] font-bold uppercase tracking-wider text-[#777D76]">
                    Courses ({results.courses.length})
                  </span>
                  <div className="mt-1 space-y-1">
                    {results.courses.map((course) => (
                      <button
                        key={course.id}
                        type="button"
                        onClick={() => {
                          clearSearch();
                          onSelectCourse?.(course.id);
                        }}
                        className="flex w-full items-center justify-between rounded-lg p-2 text-left text-xs text-[#20251F] hover:bg-[#F8F8F5]"
                      >
                        <div>
                          <div className="font-semibold">{course.title}</div>
                          <div className="text-[11px] text-[#777D76]">
                            {course.difficulty} &bull; {course.category}
                          </div>
                        </div>
                        <span className="rounded bg-[#F1F2ED] px-2 py-0.5 text-[10px] text-[#777D76]">
                          {course.lesson_count} lessons
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {results.lessons.length > 0 && (
                <div>
                  <span className="px-2 text-[10px] font-bold uppercase tracking-wider text-[#777D76]">
                    Lessons ({results.lessons.length})
                  </span>
                  <div className="mt-1 space-y-1">
                    {results.lessons.map((lesson) => (
                      <button
                        key={lesson.id}
                        type="button"
                        onClick={() => {
                          clearSearch();
                          onSelectLesson?.(lesson.id, lesson.course_id);
                        }}
                        className="flex w-full items-center justify-between rounded-lg p-2 text-left text-xs text-[#20251F] hover:bg-[#F8F8F5]"
                      >
                        <div className="flex items-center gap-2">
                          <BookOpen className="h-3.5 w-3.5 text-[#176B45]" />
                          <div>
                            <div className="font-semibold">{lesson.title}</div>
                            <div className="text-[11px] text-[#777D76]">
                              {lesson.category} &bull; {lesson.duration}
                            </div>
                          </div>
                        </div>
                        <span className="text-[10px] text-[#176B45]">Read &rarr;</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
