"use client";

import React from "react";

interface ProgressIndicatorProps {
  completed: number;
  total: number;
  variant?: "linear" | "circular" | "badge";
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  completed,
  total,
  variant = "linear",
  size = "md",
  className = "",
}) => {
  const percentage = total > 0 ? Math.min(100, Math.round((completed / total) * 100)) : 0;

  if (variant === "badge") {
    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
          percentage === 100
            ? "bg-[#16834A]/10 text-[#16834A]"
            : "bg-[#F1F2ED] text-[#777D76]"
        } ${className}`}
      >
        <span>{percentage}%</span>
        <span className="text-[10px] opacity-75">
          ({completed}/{total})
        </span>
      </span>
    );
  }

  if (variant === "circular") {
    const radius = size === "sm" ? 16 : size === "lg" ? 28 : 22;
    const strokeWidth = size === "sm" ? 3 : size === "lg" ? 5 : 4;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;
    const dimension = (radius + strokeWidth) * 2;

    return (
      <div className={`relative inline-flex items-center justify-center ${className}`}>
        <svg width={dimension} height={dimension} className="-rotate-90 transform">
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            stroke="#E8EAE4"
            strokeWidth={strokeWidth}
            fill="none"
          />
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            stroke="#176B45"
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
          />
        </svg>
        <span className="absolute font-mono text-[11px] font-bold text-[#20251F]">
          {percentage}%
        </span>
      </div>
    );
  }

  return (
    <div className={`w-full ${className}`}>
      <div className="mb-1.5 flex items-center justify-between text-xs">
        <span className="text-[#777D76]">Course Progress</span>
        <span className="font-mono font-medium text-[#20251F]">
          {completed}/{total} lessons ({percentage}%)
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-[#F1F2ED]">
        <div
          className="h-full rounded-full bg-[#176B45] transition-all duration-500 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
