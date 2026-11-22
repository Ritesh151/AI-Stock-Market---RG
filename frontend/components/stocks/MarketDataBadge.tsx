"use client";

import React from "react";
import { DataFreshness } from "@/types/stock";
import { Clock, CheckCircle2, AlertCircle, HelpCircle } from "lucide-react";

interface MarketDataBadgeProps {
  status: DataFreshness;
  source?: string | null;
  className?: string;
  showSource?: boolean;
}

export function MarketDataBadge({
  status,
  source,
  className = "",
  showSource = true,
}: MarketDataBadgeProps) {
  const getBadgeConfig = () => {
    switch (status) {
      case "REAL_TIME":
        return {
          label: "Live Market",
          bg: "bg-[#16834A]/10 text-[#16834A] border-[#16834A]/30",
          dotColor: "bg-[#16834A]",
          icon: CheckCircle2,
          pulse: true,
        };
      case "DELAYED":
        return {
          label: "Delayed (~15m)",
          bg: "bg-[#D97706]/10 text-[#B45309] border-[#D97706]/30",
          dotColor: "bg-[#D97706]",
          icon: Clock,
          pulse: false,
        };
      case "END_OF_DAY":
        return {
          label: "End of Day",
          bg: "bg-[#2563EB]/10 text-[#1D4ED8] border-[#2563EB]/30",
          dotColor: "bg-[#2563EB]",
          icon: Clock,
          pulse: false,
        };
      case "HISTORICAL":
        return {
          label: "Historical",
          bg: "bg-[#64748B]/10 text-[#475569] border-[#64748B]/30",
          dotColor: "bg-[#64748B]",
          icon: Clock,
          pulse: false,
        };
      case "UNAVAILABLE":
        return {
          label: "Feed Unavailable",
          bg: "bg-[#D64A4A]/10 text-[#D64A4A] border-[#D64A4A]/30",
          dotColor: "bg-[#D64A4A]",
          icon: AlertCircle,
          pulse: false,
        };
      case "UNKNOWN":
      default:
        return {
          label: "Unknown Status",
          bg: "bg-[#777D76]/10 text-[#777D76] border-[#777D76]/30",
          dotColor: "bg-[#777D76]",
          icon: HelpCircle,
          pulse: false,
        };
    }
  };

  const config = getBadgeConfig();
  const Icon = config.icon;

  return (
    <div className={`inline-flex items-center gap-1.5 ${className}`}>
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-medium tracking-tight ${config.bg}`}
      >
        <span className="relative flex h-1.5 w-1.5">
          {config.pulse && (
            <span
              className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${config.dotColor}`}
            />
          )}
          <span className={`relative inline-flex h-1.5 w-1.5 rounded-full ${config.dotColor}`} />
        </span>
        <Icon className="h-3 w-3" />
        <span>{config.label}</span>
      </span>

      {showSource && source && (
        <span className="text-[11px] text-[#777D76]">
          via <span className="font-medium text-[#20251F]">{source}</span>
        </span>
      )}
    </div>
  );
}
