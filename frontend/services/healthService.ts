/**
 * Health check service.
 */

import { apiClient } from "./apiClient";
import { HealthResponse } from "@/types/health";

export const healthService = {
  /**
   * Check backend health status via GET /health
   */
  async checkHealth(): Promise<HealthResponse> {
    return apiClient<HealthResponse>("/health", {
      cache: "no-store",
      timeoutMs: 4000,
    });
  },
};
