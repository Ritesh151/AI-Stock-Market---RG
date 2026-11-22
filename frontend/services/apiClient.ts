/**
 * Centralized API client.
 * Provides resilient fetch execution, timeout handling, and unified error mapping.
 */

import { appConfig } from "@/lib/config";
import { ApiError } from "@/types/api";

export class ApiClientError extends Error {
  public code: string;
  public status: number;
  public details?: unknown;

  constructor(message: string, status: number = 500, code: string = "API_ERROR", details?: unknown) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { timeoutMs = 8000, ...fetchOptions } = options;

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${appConfig.apiUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...fetchOptions.headers,
      },
    });

    clearTimeout(timer);

    const contentType = response.headers.get("content-type");
    const isJson = contentType && contentType.includes("application/json");
    const data = isJson ? await response.json() : null;

    if (!response.ok) {
      const errorPayload: ApiError | undefined = data?.error;
      throw new ApiClientError(
        errorPayload?.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        errorPayload?.code || "HTTP_ERROR",
        errorPayload?.details
      );
    }

    return data as T;
  } catch (error: unknown) {
    clearTimeout(timer);

    if (error instanceof ApiClientError) {
      throw error;
    }

    if (error instanceof Error && error.name === "AbortError") {
      throw new ApiClientError("Request timeout exceeded", 408, "TIMEOUT");
    }

    const message =
      error instanceof Error ? error.message : "Network error occurred";
    throw new ApiClientError(message, 0, "NETWORK_ERROR");
  }
}
