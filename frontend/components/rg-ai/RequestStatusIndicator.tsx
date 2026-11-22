"use client";

import React from "react";
import {
  Clock,
  RotateCw,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ShieldAlert,
  Loader2,
  StopCircle,
} from "lucide-react";
import { RequestLifecycleStatus } from "@/types/rgAi";

interface RequestStatusIndicatorProps {
  status: RequestLifecycleStatus;
  queuePosition?: number | null;
  requestId?: string;
  onCancel?: () => void;
  compact?: boolean;
}

export function RequestStatusIndicator({
  status,
  queuePosition,
  requestId,
  onCancel,
  compact = false,
}: RequestStatusIndicatorProps) {
  const getStatusConfig = () => {
    switch (status) {
      case "queued":
        return {
          label: queuePosition ? `Queued (Slot #${queuePosition})` : "Queued in Line",
          description: "Waiting for exclusive execution slot to protect persistent session...",
          color: "text-amber-800",
          bgColor: "bg-amber-50",
          borderColor: "border-amber-200",
          icon: Clock,
          animate: true,
        };
      case "initializing":
        return {
          label: "Initializing Session",
          description: "Verifying persistent browser profile and runtime lock...",
          color: "text-blue-800",
          bgColor: "bg-blue-50",
          borderColor: "border-blue-200",
          icon: RotateCw,
          animate: true,
        };
      case "waiting_for_login":
        return {
          label: "Login Required",
          description: "ChatGPT session requires authentication. Please open Chrome session to log in.",
          color: "text-orange-800",
          bgColor: "bg-orange-50",
          borderColor: "border-orange-200",
          icon: AlertCircle,
          animate: false,
        };
      case "submitting":
        return {
          label: "Submitting Prompt",
          description: "Dispatching analysis parameters to integration adapter...",
          color: "text-blue-800",
          bgColor: "bg-blue-50",
          borderColor: "border-blue-200",
          icon: RotateCw,
          animate: true,
        };
      case "processing":
        return {
          label: "Synthesizing Market Intelligence",
          description: "Generating deep equity research and technical indicators...",
          color: "text-[#176B45]",
          bgColor: "bg-[#176B45]/10",
          borderColor: "border-[#176B45]/30",
          icon: Loader2,
          animate: true,
        };
      case "validating":
        return {
          label: "Validating Strict Schema",
          description: "Applying Pydantic schema validation and financial consistency checks...",
          color: "text-purple-800",
          bgColor: "bg-purple-50",
          borderColor: "border-purple-200",
          icon: RotateCw,
          animate: true,
        };
      case "completed":
        return {
          label: "Verified Result",
          description: "Successfully validated against target JSON schema.",
          color: "text-[#16834A]",
          bgColor: "bg-[#16834A]/10",
          borderColor: "border-[#16834A]/30",
          icon: CheckCircle2,
          animate: false,
        };
      case "failed":
        return {
          label: "Execution Error",
          description: "Request failed validation or encountered an engine error.",
          color: "text-[#D64A4A]",
          bgColor: "bg-[#D64A4A]/10",
          borderColor: "border-[#D64A4A]/30",
          icon: XCircle,
          animate: false,
        };
      case "cancelled":
        return {
          label: "Request Cancelled",
          description: "Cancelled by user before completion.",
          color: "text-gray-600",
          bgColor: "bg-gray-50",
          borderColor: "border-gray-200",
          icon: StopCircle,
          animate: false,
        };
      case "integration_unavailable":
        return {
          label: "Direct Chrome Session Required",
          description: "Direct ChatGPT website scraping is disabled. Use the persistent Chrome drawer.",
          color: "text-[#777D76]",
          bgColor: "bg-[#F1F2ED]",
          borderColor: "border-[#E8EAE4]",
          icon: ShieldAlert,
          animate: false,
        };
      case "idle":
      default:
        return {
          label: "Idle",
          description: "Ready for analysis request.",
          color: "text-[#777D76]",
          bgColor: "bg-[#F8F8F5]",
          borderColor: "border-[#E8EAE4]",
          icon: Clock,
          animate: false,
        };
    }
  };

  const config = getStatusConfig();
  const IconComponent = config.icon;
  const isInFlight = [
    "queued",
    "initializing",
    "waiting_for_login",
    "submitting",
    "processing",
    "validating",
  ].includes(status);

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-medium border ${config.bgColor} ${config.color} ${config.borderColor}`}
      >
        <IconComponent
          className={`h-3 w-3 ${config.animate ? "animate-spin" : ""}`}
        />
        <span>{config.label}</span>
      </span>
    );
  }

  return (
    <div
      className={`flex items-center justify-between rounded-xl border p-3 text-xs ${config.bgColor} ${config.borderColor}`}
    >
      <div className="flex items-start gap-2.5">
        <IconComponent
          className={`h-4 w-4 shrink-0 mt-0.5 ${config.color} ${
            config.animate ? "animate-spin" : ""
          }`}
        />
        <div>
          <div className="flex items-center gap-2">
            <span className={`font-semibold ${config.color}`}>
              {config.label}
            </span>
            {requestId && (
              <span className="font-mono text-[10px] text-[#777D76]">
                {requestId}
              </span>
            )}
          </div>
          <p className="text-[11px] text-[#777D76] mt-0.5">
            {config.description}
          </p>
        </div>
      </div>

      {isInFlight && onCancel && (
        <button
          onClick={onCancel}
          className="ml-3 shrink-0 rounded-lg border border-[#D64A4A]/30 bg-white px-2.5 py-1 text-[11px] font-medium text-[#D64A4A] hover:bg-[#D64A4A]/10 transition-colors cursor-pointer"
        >
          Cancel
        </button>
      )}
    </div>
  );
}
