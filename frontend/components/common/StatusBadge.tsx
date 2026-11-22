import React from "react";
import { cn } from "@/lib/utils";

export interface StatusBadgeProps {
  status: "online" | "offline" | "checking" | "warning";
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const styles = {
    online: "bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-400 dark:border-emerald-800",
    offline: "bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/40 dark:text-rose-400 dark:border-rose-800",
    checking: "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/40 dark:text-amber-400 dark:border-amber-800",
    warning: "bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/40 dark:text-orange-400 dark:border-orange-800",
  }[status];

  const dotStyles = {
    online: "bg-emerald-500",
    offline: "bg-rose-500",
    checking: "bg-amber-500 animate-pulse",
    warning: "bg-orange-500",
  }[status];

  const displayLabel = label || {
    online: "Operational",
    offline: "Disconnected",
    checking: "Connecting...",
    warning: "Degraded",
  }[status];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border",
        styles,
        className
      )}
    >
      <span className={cn("h-1.5 w-1.5 rounded-full", dotStyles)} />
      {displayLabel}
    </span>
  );
}
