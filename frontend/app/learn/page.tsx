"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "motion/react";
import { Loader2, AlertCircle } from "lucide-react";
import {
  CategoryInfo,
  CourseDetail,
  CourseSummary,
  LessonDetail,
  UserLearningProgress,
} from "@/features/learning/types/learning";
import {
  fetchCategories,
  fetchCourseDetail,
  fetchCourses,
  fetchLessonDetail,
  fetchUserProgress,
} from "@/features/learning/services/learningApi";
import { LearningDashboard } from "@/features/learning/components/LearningDashboard";
import { LessonViewer } from "@/features/learning/components/LessonViewer";
import { pageContainerVariants } from "@/lib/motionTokens";

function LearnPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const courseParam = searchParams.get("course");
  const lessonParam = searchParams.get("lesson");

  const [courses, setCourses] = useState<CourseSummary[]>([]);
  const [categories, setCategories] = useState<CategoryInfo[]>([]);
  const [progress, setProgress] = useState<UserLearningProgress>({
    user_id: "guest_user",
    completed_lesson_ids: [],
    in_progress_course_ids: [],
    completed_course_ids: [],
    quiz_scores: {},
    bookmarked_lesson_ids: [],
    is_local_session: true,
    updated_at: new Date().toISOString(),
  });

  const [selectedCourseDetail, setSelectedCourseDetail] = useState<CourseDetail | null>(null);
  const [selectedLessonDetail, setSelectedLessonDetail] = useState<LessonDetail | null>(null);

  const [loading, setLoading] = useState(true);
  const [viewerLoading, setViewerLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initial load of catalog and progress
  useEffect(() => {
    let mounted = true;

    async function loadInitialData() {
      try {
        setLoading(true);
        const [courseList, categoryList, userProg] = await Promise.all([
          fetchCourses(),
          fetchCategories(),
          fetchUserProgress(),
        ]);
        if (mounted) {
          setCourses(courseList);
          setCategories(categoryList);
          setProgress(userProg);
        }
      } catch (err: unknown) {
        if (mounted) {
          const msg = err instanceof Error ? err.message : "Failed to load learning catalog";
          setError(msg);
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadInitialData();
    return () => {
      mounted = false;
    };
  }, []);

  // Sync with URL query parameters for course/lesson deep-linking
  useEffect(() => {
    let mounted = true;

    async function loadSelectedLesson(cId: string, lId: string) {
      setViewerLoading(true);
      try {
        const [courseData, lessonData] = await Promise.all([
          fetchCourseDetail(cId),
          fetchLessonDetail(lId),
        ]);
        if (mounted) {
          setSelectedCourseDetail(courseData);
          setSelectedLessonDetail(lessonData);
        }
      } catch (err) {
        console.warn("Failed to load lesson/course", err);
      } finally {
        if (mounted) setViewerLoading(false);
      }
    }

    async function loadSelectedCourseOnly(cId: string) {
      setViewerLoading(true);
      try {
        const courseData = await fetchCourseDetail(cId);
        if (mounted) {
          setSelectedCourseDetail(courseData);
          // Auto-select first lesson if available
          if (courseData.lessons.length > 0) {
            const firstLesson = await fetchLessonDetail(courseData.lessons[0].id);
            setSelectedLessonDetail(firstLesson);
          }
        }
      } catch (err) {
        console.warn("Failed to load course", err);
      } finally {
        if (mounted) setViewerLoading(false);
      }
    }

    if (courseParam && lessonParam) {
      loadSelectedLesson(courseParam, lessonParam);
    } else if (courseParam) {
      loadSelectedCourseOnly(courseParam);
    }

    return () => {
      mounted = false;
    };
  }, [courseParam, lessonParam]);

  const activeCourse = courseParam ? selectedCourseDetail : null;
  const activeLesson = courseParam ? selectedLessonDetail : null;

  const handleSelectCourse = (courseId: string) => {
    router.push(`/learn?course=${encodeURIComponent(courseId)}`);
  };

  const handleSelectLesson = (lessonId: string, courseId: string) => {
    router.push(
      `/learn?course=${encodeURIComponent(courseId)}&lesson=${encodeURIComponent(lessonId)}`
    );
  };

  const handleBackToDashboard = () => {
    setSelectedCourseDetail(null);
    setSelectedLessonDetail(null);
    router.push("/learn");
  };

  const handleProgressUpdated = (updated: UserLearningProgress) => {
    setProgress(updated);
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center space-y-3">
        <Loader2 className="h-8 w-8 animate-spin text-[#176B45]" />
        <p className="text-xs text-[#777D76]">
          Loading Indian Stock Market Academy...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-xl py-12">
        <div className="rounded-2xl border border-[#D64A4A]/20 bg-[#D64A4A]/5 p-6 text-center">
          <AlertCircle className="mx-auto h-8 w-8 text-[#D64A4A]" />
          <h2 className="mt-3 font-serif text-lg font-bold text-[#20251F]">
            Could Not Load Learning Data
          </h2>
          <p className="mt-1 text-xs text-[#777D76]">{error}</p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-4 rounded-xl bg-[#176B45] px-4 py-2 text-xs font-semibold text-white hover:bg-[#125837]"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      variants={pageContainerVariants}
      initial="initial"
      animate="animate"
      className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8"
    >
      <AnimatePresence mode="wait">
        {activeCourse && activeLesson ? (
          <motion.div
            key="viewer"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {viewerLoading ? (
              <div className="flex min-h-[40vh] items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-[#176B45]" />
              </div>
            ) : (
              <LessonViewer
                course={activeCourse}
                lesson={activeLesson}
                progress={progress}
                onNavigateLesson={(nextLid) =>
                  handleSelectLesson(nextLid, activeCourse.id)
                }
                onBackToDashboard={handleBackToDashboard}
                onProgressUpdated={handleProgressUpdated}
              />
            )}
          </motion.div>
        ) : (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <LearningDashboard
              courses={courses}
              categories={categories}
              progress={progress}
              onSelectCourse={handleSelectCourse}
              onSelectLesson={handleSelectLesson}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function LearnPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[60vh] flex-col items-center justify-center space-y-3">
          <Loader2 className="h-8 w-8 animate-spin text-[#176B45]" />
          <p className="text-xs text-[#777D76]">
            Initializing Learning Experience...
          </p>
        </div>
      }
    >
      <LearnPageContent />
    </Suspense>
  );
}
