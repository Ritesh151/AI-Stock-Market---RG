import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#F8F8F5",
};

export const metadata: Metadata = {
  title: "RG AI — Indian Stock Market Intelligence Platform",
  description:
    "Premium AI-powered Indian stock market intelligence platform providing technical analytics, market sentiment, and research workflows.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full bg-[#F8F8F5] text-[#20251F] selection:bg-[#176B45]/15 selection:text-[#176B45]">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
