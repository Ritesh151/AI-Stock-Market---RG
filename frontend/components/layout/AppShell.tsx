"use client";

import React, { useState } from "react";
import { Sidebar } from "./Sidebar";
import { AppHeader } from "./AppHeader";
import { AmbientBackground } from "./AmbientBackground";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [isCollapsed, setIsCollapsed] = useState<boolean>(false);
  const [isMobileOpen, setIsMobileOpen] = useState<boolean>(false);

  return (
    <div className="relative flex min-h-screen w-full bg-[#F8F8F5] text-[#20251F]">
      <AmbientBackground />

      {/* Navigation Sidebar */}
      <Sidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed((prev) => !prev)}
        isMobileOpen={isMobileOpen}
        onCloseMobile={() => setIsMobileOpen(false)}
      />

      {/* Main Content Viewport */}
      <div className="flex flex-1 flex-col overflow-x-hidden">
        <AppHeader onOpenMobileNav={() => setIsMobileOpen(true)} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
