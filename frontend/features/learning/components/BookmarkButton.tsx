"use client";

import React, { useState } from "react";
import { Bookmark } from "lucide-react";
import { addLessonBookmark, removeLessonBookmark } from "../services/learningApi";

interface BookmarkButtonProps {
  lessonId: string;
  initialBookmarked?: boolean;
  onBookmarkToggled?: (isBookmarked: boolean) => void;
  className?: string;
}

export const BookmarkButton: React.FC<BookmarkButtonProps> = ({
  lessonId,
  initialBookmarked = false,
  onBookmarkToggled,
  className = "",
}) => {
  const [isBookmarked, setIsBookmarked] = useState(initialBookmarked);
  const [loading, setLoading] = useState(false);

  const toggleBookmark = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (loading) return;
    setLoading(true);

    const nextState = !isBookmarked;
    setIsBookmarked(nextState);

    try {
      if (nextState) {
        await addLessonBookmark(lessonId);
      } else {
        await removeLessonBookmark(lessonId);
      }
      if (onBookmarkToggled) {
        onBookmarkToggled(nextState);
      }
    } catch (err) {
      console.warn("Failed to toggle bookmark", err);
      setIsBookmarked(!nextState); // Rollback
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={toggleBookmark}
      disabled={loading}
      aria-label={isBookmarked ? "Remove Bookmark" : "Save Lesson"}
      title={isBookmarked ? "Remove Bookmark" : "Save Lesson"}
      className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs font-medium transition-all ${
        isBookmarked
          ? "border-[#176B45] bg-[#176B45]/10 text-[#176B45]"
          : "border-[#E8EAE4] bg-[#FFFFFF] text-[#777D76] hover:border-[#176B45]/40 hover:text-[#20251F]"
      } ${className}`}
    >
      <Bookmark
        className={`h-4 w-4 transition-transform ${
          isBookmarked ? "fill-[#176B45]" : ""
        }`}
      />
      <span>{isBookmarked ? "Saved" : "Save"}</span>
    </button>
  );
};
