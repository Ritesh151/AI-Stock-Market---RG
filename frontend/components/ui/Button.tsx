"use client";

import React from "react";
import { motion, HTMLMotionProps } from "motion/react";
import { cn } from "@/lib/utils";
import { snappyTransition } from "@/lib/motionTokens";

export interface ButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  className,
  ...props
}: ButtonProps) {
  const variantStyles = {
    primary:
      "bg-[#176B45] text-white hover:bg-[#125436] shadow-xs border border-transparent",
    secondary:
      "bg-[#F1F2ED] text-[#20251F] hover:bg-[#E8EAE4] border border-[#E8EAE4]",
    outline:
      "bg-transparent text-[#20251F] border border-[#E8EAE4] hover:bg-[#F1F2ED]",
    ghost:
      "bg-transparent text-[#777D76] hover:bg-[#F1F2ED] hover:text-[#20251F] border border-transparent",
  }[variant];

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs rounded-lg gap-1.5",
    md: "px-4 py-2 text-sm rounded-xl gap-2",
    lg: "px-5 py-2.5 text-base rounded-xl gap-2.5",
  }[size];

  return (
    <motion.button
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.98 }}
      transition={snappyTransition}
      className={cn(
        "inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-[#176B45]/20 disabled:pointer-events-none disabled:opacity-50 cursor-pointer",
        sizeStyles,
        variantStyles,
        className
      )}
      {...props}
    >
      {children}
    </motion.button>
  );
}
