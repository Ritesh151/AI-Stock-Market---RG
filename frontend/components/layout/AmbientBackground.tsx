"use client";

import React from "react";

export function AmbientBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      {/* Primary Soft Radial Illumination */}
      <div
        className="animate-ambient-glow absolute -top-[20%] left-[15%] h-[580px] w-[580px] rounded-full blur-[120px]"
        style={{
          background:
            "radial-gradient(circle, rgba(23, 107, 69, 0.05) 0%, rgba(241, 242, 237, 0.7) 60%, transparent 100%)",
        }}
      />

      {/* Secondary Ambient Warm Light */}
      <div
        className="animate-ambient-glow absolute -bottom-[10%] right-[10%] h-[500px] w-[500px] rounded-full blur-[140px]"
        style={{
          animationDelay: "-6s",
          background:
            "radial-gradient(circle, rgba(241, 242, 237, 0.9) 0%, rgba(232, 234, 228, 0.4) 60%, transparent 100%)",
        }}
      />

      {/* Subtle Floating Decorative Elements */}
      <div
        className="animate-subtle-float absolute top-[18%] right-[8%] h-24 w-24 rounded-full border border-[#E8EAE4]/60 opacity-40"
        style={{ animationDuration: "10s" }}
      />
      <div
        className="animate-subtle-float absolute bottom-[22%] left-[5%] h-16 w-16 rounded-full border border-[#E8EAE4]/50 opacity-30"
        style={{ animationDuration: "14s", animationDelay: "-3s" }}
      />
    </div>
  );
}
