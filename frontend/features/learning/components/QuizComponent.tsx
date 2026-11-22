"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  RotateCcw,
  Send,
  Loader2,
  Award,
  Sparkles,
} from "lucide-react";
import { QuizPublic, QuizSubmissionResult } from "../types/learning";
import { submitQuizAnswers } from "../services/learningApi";

interface QuizComponentProps {
  quiz: QuizPublic;
  onQuizCompleted?: (scorePercentage: number) => void;
  className?: string;
}

export const QuizComponent: React.FC<QuizComponentProps> = ({
  quiz,
  onQuizCompleted,
  className = "",
}) => {
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<QuizSubmissionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSelect = (questionId: string, optionId: string) => {
    if (result) return; // Locked once submitted until retry
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: optionId,
    }));
  };

  const allAnswered =
    quiz.questions.length > 0 &&
    quiz.questions.every((q) => selectedAnswers[q.id]);

  const handleSubmit = async () => {
    if (!allAnswered || submitting) return;
    setSubmitting(true);
    setError(null);

    try {
      const answersList = Object.entries(selectedAnswers).map(
        ([question_id, selected_option_id]) => ({
          question_id,
          selected_option_id,
        })
      );
      const res = await submitQuizAnswers(quiz.id, answersList);
      setResult(res);
      if (onQuizCompleted) {
        onQuizCompleted(res.score_percentage);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Grading failed";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetry = () => {
    setSelectedAnswers({});
    setResult(null);
    setError(null);
  };

  return (
    <div
      className={`rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs ${className}`}
    >
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3 border-b border-[#E8EAE4] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#176B45]/10 text-[#176B45]">
              <HelpCircle className="h-4 w-4" />
            </span>
            <h3 className="font-serif text-lg font-bold text-[#20251F]">
              {quiz.title}
            </h3>
          </div>
          <p className="mt-1 text-xs text-[#777D76]">
            Pass requirement: {quiz.passing_score_percent}% &bull; Deterministic backend grading
          </p>
        </div>

        {result && (
          <div
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 font-mono text-sm font-bold ${
              result.passed
                ? "bg-[#16834A]/10 text-[#16834A]"
                : "bg-[#D64A4A]/10 text-[#D64A4A]"
            }`}
          >
            {result.passed ? (
              <Award className="h-5 w-5" />
            ) : (
              <XCircle className="h-5 w-5" />
            )}
            <span>
              {result.score_percentage}% Score ({result.correct_count}/
              {result.total_questions})
            </span>
          </div>
        )}
      </div>

      {/* Error alert */}
      {error && (
        <div className="mb-4 rounded-xl border border-[#D64A4A]/20 bg-[#D64A4A]/5 p-3 text-xs text-[#D64A4A]">
          {error}
        </div>
      )}

      {/* Questions list */}
      <div className="space-y-6">
        {quiz.questions.map((question, qIdx) => {
          const feedback = result?.feedback.find(
            (f) => f.question_id === question.id
          );
          const userChoice = selectedAnswers[question.id];

          return (
            <div
              key={question.id}
              className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5]/60 p-4 transition-colors"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <span className="mb-1 inline-block text-[11px] font-semibold uppercase tracking-wider text-[#777D76]">
                    Question {qIdx + 1} &bull; {question.question_type.replace("_", " ")}
                  </span>
                  <p className="text-sm font-semibold text-[#20251F]">
                    {question.question}
                  </p>
                  {question.scenario_context && (
                    <div className="mt-2 rounded-md bg-[#FFFFFF] p-2 text-xs text-[#777D76] border border-[#E8EAE4]">
                      <span className="font-medium text-[#20251F]">Market Scenario: </span>
                      {question.scenario_context}
                    </div>
                  )}
                </div>

                {feedback && (
                  <div className="shrink-0">
                    {feedback.is_correct ? (
                      <span className="flex items-center gap-1 text-xs font-semibold text-[#16834A]">
                        <CheckCircle2 className="h-4 w-4" /> Correct
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-xs font-semibold text-[#D64A4A]">
                        <XCircle className="h-4 w-4" /> Incorrect
                      </span>
                    )}
                  </div>
                )}
              </div>

              {/* Options */}
              <div className="mt-4 space-y-2">
                {question.options.map((opt) => {
                  const isSelected = userChoice === opt.id;
                  let optStyle =
                    "border-[#E8EAE4] bg-[#FFFFFF] text-[#20251F] hover:border-[#176B45]/40 hover:bg-[#F8F8F5]";

                  if (result && feedback) {
                    if (opt.id === feedback.correct_option_id) {
                      optStyle =
                        "border-[#16834A] bg-[#16834A]/10 text-[#16834A] font-medium";
                    } else if (isSelected && !feedback.is_correct) {
                      optStyle =
                        "border-[#D64A4A] bg-[#D64A4A]/10 text-[#D64A4A]";
                    } else {
                      optStyle = "border-[#E8EAE4] bg-[#FFFFFF] opacity-50";
                    }
                  } else if (isSelected) {
                    optStyle =
                      "border-[#176B45] bg-[#176B45]/5 text-[#176B45] font-semibold";
                  }

                  return (
                    <button
                      key={opt.id}
                      type="button"
                      disabled={Boolean(result)}
                      onClick={() => handleSelect(question.id, opt.id)}
                      className={`flex w-full items-center justify-between rounded-xl border p-3 text-left text-xs transition-all ${optStyle}`}
                    >
                      <span className="flex items-center gap-2.5">
                        <span
                          className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[10px] font-bold ${
                            isSelected
                              ? "border-[#176B45] bg-[#176B45] text-white"
                              : "border-[#777D76]/40 text-[#777D76]"
                          }`}
                        >
                          {opt.id.replace("opt-", "").toUpperCase()}
                        </span>
                        <span>{opt.text}</span>
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Explanation Reveal */}
              <AnimatePresence>
                {feedback && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-3 overflow-hidden rounded-lg bg-[#FFFFFF] p-3 text-xs border border-[#E8EAE4]"
                  >
                    <span className="font-bold text-[#20251F]">Explanation: </span>
                    <span className="text-[#777D76]">{feedback.explanation}</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>

      {/* Action footer */}
      <div className="mt-6 flex flex-wrap items-center justify-between gap-3 border-t border-[#E8EAE4] pt-4">
        {!result ? (
          <div className="flex w-full items-center justify-between">
            <span className="text-xs text-[#777D76]">
              {Object.keys(selectedAnswers).length} of {quiz.questions.length}{" "}
              answered
            </span>
            <button
              type="button"
              disabled={!allAnswered || submitting}
              onClick={handleSubmit}
              className="inline-flex items-center gap-2 rounded-xl bg-[#176B45] px-5 py-2.5 text-xs font-semibold text-white shadow-xs transition-all hover:bg-[#125837] disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Grading on Backend...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  Submit Quiz
                </>
              )}
            </button>
          </div>
        ) : (
          <div className="flex w-full flex-wrap items-center justify-between gap-3">
            <div className="text-xs text-[#777D76]">
              {result.passed ? (
                <span className="flex items-center gap-1.5 font-medium text-[#16834A]">
                  <Sparkles className="h-4 w-4" />
                  Great job! You passed the knowledge check.
                </span>
              ) : (
                <span className="text-[#D64A4A]">
                  Score is below {quiz.passing_score_percent}%. Review explanations and retry.
                </span>
              )}
            </div>
            <button
              type="button"
              onClick={handleRetry}
              className="inline-flex items-center gap-2 rounded-xl border border-[#E8EAE4] bg-[#FFFFFF] px-4 py-2 text-xs font-semibold text-[#20251F] hover:bg-[#F8F8F5]"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Retry Quiz
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
