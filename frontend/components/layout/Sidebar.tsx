"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "motion/react";
import {
  LayoutDashboard,
  TrendingUp,
  Bot,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { snappyTransition, standardTransition } from "@/lib/motionTokens";

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const navItems: NavItem[] = [
  {
    title: "Overview",
    href: "/",
    icon: LayoutDashboard,
  },
  {
    title: "Stock Price",
    href: "/stocks",
    icon: TrendingUp,
  },
  {
    title: "RG AI",
    href: "/rg-ai",
    icon: Bot,
    badge: "AI",
  },
  {
    title: "Learn Trading",
    href: "/learn",
    icon: BookOpen,
  },
];

interface SidebarProps {
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  isMobileOpen: boolean;
  onCloseMobile: () => void;
}

export function Sidebar({
  isCollapsed,
  onToggleCollapse,
  isMobileOpen,
  onCloseMobile,
}: SidebarProps) {
  const pathname = usePathname();

  const isCurrentActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  const navContent = (
    <div className="flex h-full flex-col justify-between p-4">
      {/* Top: Logo & Nav items */}
      <div className="space-y-6">
        {/* Brand */}
        <div className="flex items-center justify-between px-2">
          <Link href="/" className="flex items-center gap-2.5 overflow-hidden">
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#176B45] text-white shadow-sm"
            >
              <span className="font-bold text-sm tracking-tight">RG</span>
            </motion.div>
            <AnimatePresence mode="wait">
              {!isCollapsed && (
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -10 }}
                  transition={snappyTransition}
                  className="whitespace-nowrap"
                >
                  <div className="font-semibold text-sm text-[#20251F]">RG AI</div>
                  <div className="text-[11px] text-[#777D76]">Indian Market Intel</div>
                </motion.div>
              )}
            </AnimatePresence>
          </Link>

          {/* Mobile close button */}
          <button
            onClick={onCloseMobile}
            className="rounded-lg p-1 text-[#777D76] hover:bg-[#F1F2ED] md:hidden"
            aria-label="Close navigation"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation list */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const active = isCurrentActive(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onCloseMobile}
                className={cn(
                  "relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                  active
                    ? "text-[#176B45]"
                    : "text-[#777D76] hover:bg-[#F1F2ED]/80 hover:text-[#20251F]"
                )}
              >
                {/* Active Sliding Pill Indicator */}
                {active && (
                  <motion.div
                    layoutId="activeNavIndicator"
                    className="absolute inset-0 rounded-xl bg-[#F1F2ED] border border-[#E8EAE4]"
                    transition={standardTransition}
                  />
                )}

                <span className="relative z-10 flex shrink-0 items-center justify-center">
                  <Icon
                    className={cn(
                      "h-5 w-5 transition-transform duration-200",
                      active ? "text-[#176B45] scale-105" : "text-[#777D76]"
                    )}
                  />
                </span>

                <AnimatePresence mode="wait">
                  {!isCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: "auto" }}
                      exit={{ opacity: 0, width: 0 }}
                      transition={snappyTransition}
                      className="relative z-10 flex flex-1 items-center justify-between overflow-hidden whitespace-nowrap"
                    >
                      <span>{item.title}</span>
                      {item.badge && (
                        <span className="rounded-md bg-[#176B45]/10 px-1.5 py-0.5 text-[10px] font-semibold text-[#176B45]">
                          {item.badge}
                        </span>
                      )}
                    </motion.span>
                  )}
                </AnimatePresence>
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom: Profile card & Collapse toggle */}
      <div className="space-y-3 pt-4 border-t border-[#E8EAE4]">
        <div
          className={cn(
            "flex items-center gap-3 rounded-xl bg-[#FFFFFF] p-2.5 border border-[#E8EAE4] shadow-xs",
            isCollapsed && "justify-center p-2"
          )}
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[#F1F2ED] text-[#176B45]">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: "auto" }}
                exit={{ opacity: 0, width: 0 }}
                transition={snappyTransition}
                className="overflow-hidden whitespace-nowrap"
              >
                <div className="text-xs font-semibold text-[#20251F]">NSE &bull; BSE Pro</div>
                <div className="text-[10px] text-[#777D76]">Phase 2 &bull; Active</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Desktop Collapse Trigger */}
        <button
          onClick={onToggleCollapse}
          className="hidden w-full items-center justify-center rounded-xl p-2 text-[#777D76] transition-colors hover:bg-[#F1F2ED] hover:text-[#20251F] md:flex"
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <div className="flex w-full items-center justify-between px-2 text-xs font-medium">
              <span>Collapse</span>
              <ChevronLeft className="h-4 w-4" />
            </div>
          )}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <motion.aside
        animate={{ width: isCollapsed ? 76 : 240 }}
        transition={standardTransition}
        className="hidden shrink-0 border-r border-[#E8EAE4] bg-[#F8F8F5]/90 backdrop-blur-md md:block"
      >
        {navContent}
      </motion.aside>

      {/* Mobile Drawer Backdrop & Slide-out */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={snappyTransition}
              onClick={onCloseMobile}
              className="fixed inset-0 z-40 bg-[#20251F]/20 backdrop-blur-xs md:hidden"
            />
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={standardTransition}
              className="fixed inset-y-0 left-0 z-50 w-64 border-r border-[#E8EAE4] bg-[#F8F8F5] shadow-xl md:hidden"
            >
              {navContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
