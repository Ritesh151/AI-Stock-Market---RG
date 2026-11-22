"use client";

import { useEffect, useState, useCallback } from "react";
import { healthService } from "@/services/healthService";
import { HealthResponse } from "@/types/health";

export type HealthStatus = "checking" | "online" | "offline";

export function useHealthCheck(pollIntervalMs = 0) {
  const [status, setStatus] = useState<HealthStatus>("checking");
  const [data, setData] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const check = useCallback(async () => {
    try {
      const response = await healthService.checkHealth();
      setData(response);
      setStatus(response.success && response.status === "healthy" ? "online" : "offline");
      setError(null);
    } catch (err: unknown) {
      setStatus("offline");
      setError(err instanceof Error ? err.message : "Unable to reach backend");
    }
  }, []);

  useEffect(() => {
    let isCancelled = false;

    async function execute() {
      try {
        const response = await healthService.checkHealth();
        if (!isCancelled) {
          setData(response);
          setStatus(response.success && response.status === "healthy" ? "online" : "offline");
          setError(null);
        }
      } catch (err: unknown) {
        if (!isCancelled) {
          setStatus("offline");
          setError(err instanceof Error ? err.message : "Unable to reach backend");
        }
      }
    }

    void execute();

    if (pollIntervalMs > 0) {
      const timer = setInterval(() => {
        void execute();
      }, pollIntervalMs);
      return () => {
        isCancelled = true;
        clearInterval(timer);
      };
    }

    return () => {
      isCancelled = true;
    };
  }, [pollIntervalMs]);

  return { status, data, error, refresh: check };
}
