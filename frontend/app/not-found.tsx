import React from "react";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-100 font-mono text-xl font-bold text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200">
        404
      </div>
      <h2 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
        Page Not Found
      </h2>
      <p className="mt-2 max-w-md text-sm text-zinc-600 dark:text-zinc-400">
        The requested resource does not exist in the RG AI Indian Stock Market Intelligence Platform.
      </p>
      <div className="mt-6">
        <Link
          href="/"
          className="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700"
        >
          Return to Platform Home
        </Link>
      </div>
    </div>
  );
}
