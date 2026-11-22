"use client";

import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Globe,
  ShieldCheck,
  ExternalLink,
  Power,
  RotateCw,
  CheckCircle2,
  Lock,
  Loader2,
  AlertTriangle,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  browserService,
  BrowserStatus,
} from "@/services/browserService";
import { snappyTransition } from "@/lib/motionTokens";

interface BrowserConnectionCardProps {
  onStatusChange?: (status: BrowserStatus) => void;
  className?: string;
}

export function BrowserConnectionCard({
  onStatusChange,
  className,
}: BrowserConnectionCardProps) {
  const [status, setStatus] = useState<BrowserStatus | null>(null);
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await browserService.getStatus();
      setStatus(res);
      setErrorMessage(null);
      if (onStatusChange) onStatusChange(res);
    } catch {
      setErrorMessage("Unable to connect to backend browser service.");
    }
  }, [onStatusChange]);

  useEffect(() => {
    let isMounted = true;

    const load = async () => {
      try {
        const res = await browserService.getStatus();
        if (isMounted) {
          setStatus(res);
          setErrorMessage(null);
          if (onStatusChange) onStatusChange(res);
        }
      } catch {
        if (isMounted) {
          setErrorMessage("Unable to connect to backend browser service.");
        }
      }
    };

    void load();
    const interval = setInterval(() => {
      void load();
    }, 8000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [onStatusChange]);

  const handleAction = async (actionName: string, actionFn: () => Promise<{ message: string }>) => {
    if (loadingAction) return; // Prevent duplicate submission
    setLoadingAction(actionName);
    setActionMessage(null);
    setErrorMessage(null);

    try {
      const result = await actionFn();
      setActionMessage(result.message);
      await fetchStatus();
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "Browser operation failed. Please check backend logs."
      );
    } finally {
      setLoadingAction(null);
    }
  };

  const isRunning = status?.is_running ?? false;
  const loginState = status?.login_status ?? "UNKNOWN";
  const state = status?.state ?? "STOPPED";

  // Compute primary button label & state
  const getPrimaryButtonState = () => {
    if (loadingAction === "start") return { label: "Starting Chrome...", disabled: true };
    if (state === "ERROR") return { label: "Retry Connection", disabled: false, action: "reconnect" };
    if (!isRunning) return { label: "Connect Browser", disabled: false, action: "start" };
    if (loginState === "AUTHENTICATED") return { label: "Connected", disabled: true, action: "none" };
    if (loginState === "LOGIN_REQUIRED") return { label: "Complete Login", disabled: false, action: "open_gpt" };
    return { label: "Browser Active", disabled: false, action: "open_gpt" };
  };

  const primaryBtn = getPrimaryButtonState();

  return (
    <Card className={`p-5 border border-[#E8EAE4] bg-[#FFFFFF] space-y-5 ${className}`}>
      {/* Header bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-[#E8EAE4] pb-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#F1F2ED] text-[#176B45]">
            <Globe className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-semibold text-sm text-[#20251F]">
                Chrome Playwright Session
              </h2>
              <span className="rounded bg-[#176B45]/10 px-2 py-0.5 text-[10px] font-semibold text-[#176B45]">
                Persistent Profile
              </span>
            </div>
            <p className="text-[11px] text-[#777D76]">
              Zero-OpenAI API &bull; User-in-the-Loop Browser Authentication
            </p>
          </div>
        </div>

        {/* Status badges */}
        <div className="flex flex-wrap items-center gap-2">
          <Badge
            variant={isRunning ? "positive" : state === "ERROR" ? "negative" : "neutral"}
            size="sm"
          >
            Chrome: {state}
          </Badge>

          <Badge
            variant={
              loginState === "AUTHENTICATED"
                ? "positive"
                : loginState === "LOGIN_REQUIRED"
                ? "accent"
                : "neutral"
            }
            size="sm"
          >
            ChatGPT: {loginState}
          </Badge>
        </div>
      </div>

      {/* Target URL & Profile Invariants Info */}
      <div className="rounded-xl border border-[#E8EAE4] bg-[#F1F2ED]/40 p-3.5 space-y-2 text-xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 text-[11px]">
          <span className="font-medium text-[#777D76]">Fixed Target Assistant:</span>
          <span className="font-mono text-[#20251F] truncate max-w-md">
            {status?.target_url || "https://chatgpt.com/g/g-jkxrUFNja-indian-stock-market"}
          </span>
        </div>

        <div className="flex items-center justify-between text-[11px] text-[#777D76]">
          <span className="flex items-center gap-1">
            <Lock className="h-3 w-3 text-[#176B45]" />
            Session Storage: Dedicated <code className="font-mono text-[10px]">data/chrome-profile</code>
          </span>
          {status?.last_health_check && (
            <span>
              Probe: {new Date(status.last_health_check).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
            </span>
          )}
        </div>
      </div>

      {/* Action Notification Messages */}
      <AnimatePresence mode="wait">
        {actionMessage && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={snappyTransition}
            className="flex items-center gap-2 rounded-xl bg-[#16834A]/10 border border-[#16834A]/20 p-3 text-xs text-[#16834A]"
          >
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>{actionMessage}</span>
          </motion.div>
        )}

        {errorMessage && (
          <motion.div
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={snappyTransition}
            className="flex items-center gap-2 rounded-xl bg-[#D64A4A]/10 border border-[#D64A4A]/20 p-3 text-xs text-[#D64A4A]"
          >
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{errorMessage}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Control Actions Row */}
      <div className="flex flex-wrap items-center gap-2.5 pt-1">
        {/* Primary Action Button */}
        <Button
          variant="primary"
          size="sm"
          disabled={primaryBtn.disabled || loadingAction !== null}
          onClick={() => {
            if (primaryBtn.action === "start") handleAction("start", browserService.startBrowser);
            else if (primaryBtn.action === "reconnect") handleAction("reconnect", browserService.reconnectBrowser);
            else if (primaryBtn.action === "open_gpt") handleAction("open_gpt", browserService.openTargetGpt);
          }}
        >
          {loadingAction === "start" && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
          <span>{primaryBtn.label}</span>
        </Button>

        {/* Open Target GPT Button */}
        {isRunning && (
          <Button
            variant="secondary"
            size="sm"
            disabled={loadingAction !== null}
            onClick={() => handleAction("open_gpt", browserService.openTargetGpt)}
          >
            {loadingAction === "open_gpt" ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <ExternalLink className="h-3.5 w-3.5" />
            )}
            <span>Open Custom GPT</span>
          </Button>
        )}

        {/* Confirm Login Button */}
        {isRunning && loginState !== "AUTHENTICATED" && (
          <Button
            variant="outline"
            size="sm"
            disabled={loadingAction !== null}
            onClick={() => handleAction("confirm_login", browserService.confirmLogin)}
          >
            {loadingAction === "confirm_login" ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <ShieldCheck className="h-3.5 w-3.5 text-[#176B45]" />
            )}
            <span>Confirm Login</span>
          </Button>
        )}

        {/* Stop / Disconnect Button */}
        {isRunning && (
          <Button
            variant="ghost"
            size="sm"
            disabled={loadingAction !== null}
            onClick={() => handleAction("stop", browserService.stopBrowser)}
            className="text-[#D64A4A] hover:bg-[#D64A4A]/10 ml-auto"
          >
            {loadingAction === "stop" ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Power className="h-3.5 w-3.5" />
            )}
            <span>Disconnect</span>
          </Button>
        )}

        {/* Refresh Probe Icon */}
        <button
          onClick={fetchStatus}
          disabled={loadingAction !== null}
          className="rounded-lg p-2 text-[#777D76] hover:bg-[#F1F2ED] transition-colors cursor-pointer"
          title="Refresh browser probe"
          aria-label="Refresh browser status"
        >
          <RotateCw className={`h-3.5 w-3.5 ${loadingAction ? "animate-spin" : ""}`} />
        </button>
      </div>
    </Card>
  );
}
