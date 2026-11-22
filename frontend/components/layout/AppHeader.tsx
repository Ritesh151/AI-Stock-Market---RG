"use client";

import React, { useState, useEffect } from "react";
import { Menu, Clock } from "lucide-react";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import { StatusBadge } from "@/components/common/StatusBadge";
import { motion } from "motion/react";
import { snappyTransition } from "@/lib/motionTokens";

interface AppHeaderProps {
  onOpenMobileNav: () => void;
}

export function AppHeader({ onOpenMobileNav }: AppHeaderProps) {
  const { status, refresh } = useHealthCheck(15000);
  const [istTime, setIstTime] = useState<string>("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setIstTime(
        now.toLocaleTimeString("en-IN", {
          timeZone: "Asia/Kolkata",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: true,
        })
      );
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-[#E8EAE4] bg-[#F8F8F5]/85 px-4 backdrop-blur-md sm:px-6 lg:px-8">
      {/* Left: Mobile Menu Toggle & Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileNav}
          className="rounded-lg p-2 text-[#777D76] hover:bg-[#F1F2ED] md:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm tracking-tight text-[#20251F]">
            Indian Stock Market Intelligence
          </span>
          <span className="hidden rounded-full bg-[#176B45]/10 px-2 py-0.5 text-[11px] font-medium text-[#176B45] sm:inline-block">
            NSE &bull; BSE
          </span>
        </div>
      </div>

      {/* Right: Market IST Status & Backend Connectivity */}
      <div className="flex items-center gap-3">
        {/* Market IST Clock Badge */}
        <div className="hidden items-center gap-1.5 rounded-lg border border-[#E8EAE4] bg-[#FFFFFF] px-2.5 py-1 text-xs text-[#777D76] sm:flex">
          <Clock className="h-3.5 w-3.5 text-[#176B45]" />
          <span className="font-mono text-[11px] font-medium text-[#20251F]">
            {istTime || "09:15 - 15:30 IST"}
          </span>
        </div>

        {/* Live Backend Indicator */}
        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          transition={snappyTransition}
          onClick={() => refresh()}
          className="cursor-pointer"
          title="Click to refresh system probe"
        >
          <StatusBadge
            status={status}
            label={
              status === "online"
                ? "Engine Active"
                : status === "checking"
                ? "Connecting..."
                : "Engine Offline"
            }
          />
        </motion.div>
      </div>
    </header>
  );
}
