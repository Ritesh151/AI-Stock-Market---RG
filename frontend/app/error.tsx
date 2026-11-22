"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  useEffect(() => {
    // Log error securely
    console.error("Application error captured by boundary:", error.message);
  }, [error]);

  return (
    <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-rose-100 text-rose-700 dark:bg-rose-950/50 dark:text-rose-400">
        <svg
          className="h-6 w-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
        Something went wrong
      </h2>
      <p className="mt-2 max-w-md text-sm text-zinc-600 dark:text-zinc-400">
        An unexpected error occurred while rendering the interface.
      </p>
      <div className="mt-6 flex items-center gap-3">
        <button
          onClick={() => reset()}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
        >
          Try Again
        </button>
        <button
          onClick={() => router.push("/")}
          className="rounded-lg border border-zinc-200 bg-white px-4 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-300 dark:hover:bg-zinc-800"
        >
          Go Home
        </button>
      </div>
    </div>
  );
}
