"use client";

import React from "react";
import { motion, HTMLMotionProps } from "motion/react";
import { cn } from "@/lib/utils";
import { standardTransition } from "@/lib/motionTokens";

export interface CardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  className?: string;
  enableHover?: boolean;
  isLoading?: boolean;
}

export function Card({
  children,
  className,
  enableHover = true,
  isLoading = false,
  ...props
}: CardProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          "rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs animate-pulse",
          className
        )}
      >
        <div className="h-4 w-1/3 rounded bg-[#F1F2ED]" />
        <div className="mt-4 h-8 w-1/2 rounded bg-[#F1F2ED]" />
        <div className="mt-3 h-3 w-3/4 rounded bg-[#F1F2ED]" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 12 }}
      transition={standardTransition}
      whileHover={
        enableHover
          ? {
              y: -2,
              borderColor: "#D5D8CF",
              boxShadow: "0 6px 16px -4px rgba(32, 37, 31, 0.05)",
            }
          : undefined
      }
      className={cn(
        "rounded-2xl border border-[#E8EAE4] bg-[#FFFFFF] p-6 shadow-xs transition-colors",
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}
