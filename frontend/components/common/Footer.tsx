import React from "react";

export function Footer() {
  return (
    <footer className="w-full border-t border-zinc-200 bg-white py-6 dark:border-zinc-800 dark:bg-zinc-950">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 text-xs text-zinc-500 sm:flex-row sm:px-6 lg:px-8">
        <div>
          <span>&copy; 2026 RG AI Platform. Indian Stock Market Intelligence.</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Backend: FastAPI</span>
          <span>&bull;</span>
          <span>Frontend: Next.js</span>
          <span>&bull;</span>
          <span className="font-mono">v1.0.0-phase1</span>
        </div>
      </div>
    </footer>
  );
}
