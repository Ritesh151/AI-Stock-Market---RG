import React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps {
  children: React.ReactNode;
  variant?: "positive" | "negative" | "neutral" | "accent";
  size?: "sm" | "md";
  className?: string;
  showDot?: boolean;
}

export function Badge({
  children,
  variant = "neutral",
  size = "md",
  className,
  showDot = true,
}: BadgeProps) {
  const variantStyles = {
    positive: "bg-[#16834A]/10 text-[#16834A] border-[#16834A]/20",
    negative: "bg-[#D64A4A]/10 text-[#D64A4A] border-[#D64A4A]/20",
    neutral: "bg-[#F1F2ED] text-[#777D76] border-[#E8EAE4]",
    accent: "bg-[#176B45]/10 text-[#176B45] border-[#176B45]/20",
  }[variant];

  const dotStyles = {
    positive: "bg-[#16834A]",
    negative: "bg-[#D64A4A]",
    neutral: "bg-[#777D76]",
    accent: "bg-[#176B45]",
  }[variant];

  const sizeStyles = {
    sm: "px-2 py-0.5 text-[11px]",
    md: "px-2.5 py-1 text-xs",
  }[size];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        sizeStyles,
        variantStyles,
        className
      )}
    >
      {showDot && <span className={cn("h-1.5 w-1.5 rounded-full", dotStyles)} />}
      {children}
    </span>
  );
}
