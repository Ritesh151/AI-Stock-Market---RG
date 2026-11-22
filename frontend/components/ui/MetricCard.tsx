"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card } from "./Card";
import { Badge } from "./Badge";
import { cn } from "@/lib/utils";

export interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  isPositive: boolean | null;
  subtitle?: string;
  sparklineData?: number[];
  className?: string;
}

export function MetricCard({
  title,
  value,
  change,
  isPositive,
  subtitle,
  sparklineData = [20, 24, 22, 28, 26, 32, 35],
  className,
}: MetricCardProps) {
  // Generate simple SVG sparkline path
  const min = Math.min(...sparklineData);
  const max = Math.max(...sparklineData);
  const range = max - min || 1;
  const width = 80;
  const height = 28;

  const points = sparklineData
    .map((val, idx) => {
      const x = (idx / (sparklineData.length - 1)) * width;
      const y = height - ((val - min) / range) * (height - 4) - 2;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  const color =
    isPositive === true
      ? "#16834A"
      : isPositive === false
      ? "#D64A4A"
      : "#777D76";

  return (
    <Card className={cn("p-5", className)}>
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs font-medium text-[#777D76]">{title}</span>
          <div className="mt-1 font-mono text-xl font-bold tracking-tight text-[#20251F]">
            {value}
          </div>
        </div>

        {/* Mini Sparkline */}
        <div className="shrink-0 pt-1">
          <svg width={width} height={height} className="overflow-visible">
            <polyline
              fill="none"
              stroke={color}
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              points={points}
            />
          </svg>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-[#E8EAE4] pt-3">
        <Badge
          variant={
            isPositive === true
              ? "positive"
              : isPositive === false
              ? "negative"
              : "neutral"
          }
          size="sm"
        >
          <span className="inline-flex items-center gap-1 font-mono">
            {isPositive === true && <TrendingUp className="h-3 w-3" />}
            {isPositive === false && <TrendingDown className="h-3 w-3" />}
            {isPositive === null && <Minus className="h-3 w-3" />}
            {change}
          </span>
        </Badge>

        {subtitle && (
          <span className="text-[11px] text-[#777D76]">{subtitle}</span>
        )}
      </div>
    </Card>
  );
}
