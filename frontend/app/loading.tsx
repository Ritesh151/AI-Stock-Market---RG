import React from "react";

export default function Loading() {
  return (
    <div className="flex flex-1 items-center justify-center p-8">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
          Loading RG AI Intelligence...
        </p>
      </div>
    </div>
  );
}
