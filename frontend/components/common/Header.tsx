import React from "react";
import Link from "next/link";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-200 bg-white/80 backdrop-blur-md dark:border-zinc-800 dark:bg-zinc-950/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 font-bold text-white shadow-sm">
              RG
            </div>
            <div>
              <span className="text-base font-semibold tracking-tight text-zinc-900 dark:text-zinc-100">
                RG AI
              </span>
              <span className="ml-1.5 hidden text-xs font-normal text-zinc-500 sm:inline">
                Indian Stock Market Intelligence
              </span>
            </div>
          </Link>
        </div>

        <div className="flex items-center gap-3">
          <span className="rounded border border-zinc-200 bg-zinc-100 px-2 py-0.5 text-[11px] font-mono text-zinc-600 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-400">
            Phase 1 Foundation
          </span>
        </div>
      </div>
    </header>
  );
}
