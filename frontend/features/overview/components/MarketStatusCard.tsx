"use client";

import React from "react";
import { Clock, Calendar, CheckCircle2, HelpCircle } from "lucide-react";
import { MarketStatusData } from "../types/overview";
import { Card } from "@/components/ui/Card";

interface MarketStatusCardProps {
  status: MarketStatusData | null;
}

export function MarketStatusCard({ status }: MarketStatusCardProps) {
  const isOpen = status?.status === "OPEN";
  const isPreOpen = status?.status === "PRE_OPEN";
  const isClosed = status?.status === "CLOSED";

  const getStatusBadge = () => {
    if (isOpen) {
      return {
        label: "Market Open (Regular)",
        bg: "bg-[#16834A]/10 text-[#16834A] border-[#16834A]/30",
        icon: CheckCircle2,
      };
    }
    if (isPreOpen) {
      return {
        label: "Pre-Open Session",
        bg: "bg-[#D97706]/10 text-[#B45309] border-[#D97706]/30",
        icon: Clock,
      };
    }
    if (isClosed) {
      return {
        label: "Market Closed",
        bg: "bg-[#777D76]/10 text-[#777D76] border-[#777D76]/30",
        icon: Clock,
      };
    }
    return {
      label: "Status Unknown",
      bg: "bg-[#D64A4A]/10 text-[#D64A4A] border-[#D64A4A]/30",
      icon: HelpCircle,
    };
  };

  const badge = getStatusBadge();
  const Icon = badge.icon;

  return (
    <Card className="p-5 space-y-4">
      <div className="flex items-center justify-between border-b border-[#E8EAE4] pb-3">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-[#176B45]" />
          <h3 className="font-semibold text-sm text-[#20251F]">
            Indian Exchange Schedule
          </h3>
        </div>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${badge.bg}`}
        >
          <Icon className="h-3 w-3" />
          <span>{badge.label}</span>
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3">
          <span className="text-[11px] text-[#777D76]">Standard Hours</span>
          <div className="mt-1 font-mono font-semibold text-[#20251F]">
            09:15 – 15:30 IST
          </div>
        </div>

        <div className="rounded-xl border border-[#E8EAE4] bg-[#F8F8F5] p-3">
          <span className="text-[11px] text-[#777D76]">Pre-Open Session</span>
          <div className="mt-1 font-mono font-semibold text-[#20251F]">
            09:00 – 09:08 IST
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1.5 text-[11px] text-[#777D76]">
        <Clock className="h-3 w-3 text-[#176B45]" />
        <span>Timezone: <span className="font-mono font-medium text-[#20251F]">Asia/Kolkata (IST)</span> • Verified Exchange Calendar</span>
      </div>
    </Card>
  );
}
