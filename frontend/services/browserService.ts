/**
 * Browser Automation API Service.
 * Interfaces with backend Playwright lifecycle and session management endpoints.
 */

import { apiClient } from "./apiClient";

export type BrowserState =
  | "STOPPED"
  | "STARTING"
  | "RUNNING"
  | "LOGIN_REQUIRED"
  | "AUTHENTICATED"
  | "TARGET_OPEN"
  | "DISCONNECTED"
  | "ERROR"
  | "STOPPING";

export type LoginState =
  | "UNKNOWN"
  | "LOGIN_REQUIRED"
  | "AUTHENTICATED"
  | "CHALLENGE_DETECTED";

export interface BrowserStatus {
  state: BrowserState;
  is_running: boolean;
  target_url: string;
  login_status: LoginState;
  last_health_check?: string | null;
  error_message?: string | null;
  active_pages_count: number;
  is_locked: boolean;
}

export interface BrowserActionResult {
  success: boolean;
  message: string;
  state: BrowserState;
  login_status: LoginState;
}

export const browserService = {
  async getStatus(): Promise<BrowserStatus> {
    return apiClient<BrowserStatus>("/api/v1/browser/status", {
      cache: "no-store",
      timeoutMs: 6000,
    });
  },

  async startBrowser(): Promise<BrowserActionResult> {
    return apiClient<BrowserActionResult>("/api/v1/browser/start", {
      method: "POST",
      timeoutMs: 35000,
    });
  },

  async openTargetGpt(): Promise<BrowserActionResult> {
    return apiClient<BrowserActionResult>("/api/v1/browser/open-gpt", {
      method: "POST",
      timeoutMs: 35000,
    });
  },

  async confirmLogin(): Promise<BrowserActionResult> {
    return apiClient<BrowserActionResult>("/api/v1/browser/confirm-login", {
      method: "POST",
      timeoutMs: 15000,
    });
  },

  async stopBrowser(): Promise<BrowserActionResult> {
    return apiClient<BrowserActionResult>("/api/v1/browser/stop", {
      method: "POST",
      timeoutMs: 15000,
    });
  },

  async reconnectBrowser(): Promise<BrowserActionResult> {
    return apiClient<BrowserActionResult>("/api/v1/browser/reconnect", {
      method: "POST",
      timeoutMs: 35000,
    });
  },
};
