/**
 * RG AI Orchestration & Response Service Client.
 * Interfaces with /api/v1/rg-ai/* endpoints for prompt submission, status polling, cancellation,
 * and response validation/introspection.
 */

import { apiClient } from "@/services/apiClient";
import {
  RequestLifecycleStatus,
  ResponseEnvelope,
  ValidationErrorEnvelope,
  SupportedSchemaType,
} from "@/types/rgAi";

export { type RequestLifecycleStatus } from "@/types/rgAi";

export interface ChatSubmissionResponse {
  success: boolean;
  request_id: string;
  status: RequestLifecycleStatus;
  created_at: string;
  queue_position: number;
  message: string;
}

export interface RequestStatusResponse {
  success: boolean;
  request_id: string;
  status: RequestLifecycleStatus;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  queue_position: number | null;
  result: (Record<string, unknown> & {
    content?: string;
    metadata?: Record<string, unknown>;
    format_type?: string;
    type?: string;
    data?: Record<string, unknown>;
    warnings?: string[];
    disclaimer?: string;
    schema_version?: string;
  }) | null;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  } | null;
}

export interface CancelRequestResponse {
  success: boolean;
  request_id: string;
  status: RequestLifecycleStatus;
  message: string;
}

export interface AvailabilityResponse {
  is_available: boolean;
  is_browser_running: boolean;
  login_state: string;
  target_url: string;
  adapter_type: string;
  message: string;
}

export interface EngineHealthResponse {
  status: string;
  queue_size: number;
  max_queue_size: number;
  active_worker: boolean;
  concurrency_limit: number;
  total_processed: number;
  total_failed: number;
  total_cancelled: number;
}

export interface SchemaListResponse {
  supported_types: SupportedSchemaType[];
  count: number;
}

export const rgAiService = {
  /**
   * Submits user analysis prompt to the FastAPI queue.
   */
  async submitPrompt(
    prompt: string,
    conversationId?: string,
    metadata?: Record<string, unknown>
  ): Promise<ChatSubmissionResponse> {
    return apiClient<ChatSubmissionResponse>("/api/v1/rg-ai/chat", {
      method: "POST",
      body: JSON.stringify({
        prompt,
        conversation_id: conversationId,
        metadata,
      }),
    });
  },

  /**
   * Polls real-time request lifecycle state and normalized results.
   */
  async getStatus(requestId: string): Promise<RequestStatusResponse> {
    return apiClient<RequestStatusResponse>(`/api/v1/rg-ai/status/${requestId}`, {
      method: "GET",
    });
  },

  /**
   * Cancels a queued or currently executing request.
   */
  async cancelRequest(requestId: string): Promise<CancelRequestResponse> {
    return apiClient<CancelRequestResponse>(`/api/v1/rg-ai/cancel/${requestId}`, {
      method: "POST",
    });
  },

  /**
   * Probes integration adapter capability and browser readiness.
   */
  async checkAvailability(): Promise<AvailabilityResponse> {
    return apiClient<AvailabilityResponse>("/api/v1/rg-ai/availability", {
      method: "POST",
    });
  },

  /**
   * Retrieves engine health and queue load metrics.
   */
  async getHealth(): Promise<EngineHealthResponse> {
    return apiClient<EngineHealthResponse>("/api/v1/rg-ai/health", {
      method: "GET",
    });
  },

  /**
   * Lists all supported JSON analysis schemas.
   */
  async getSchemas(): Promise<SchemaListResponse> {
    return apiClient<SchemaListResponse>("/api/v1/rg-ai/schemas", {
      method: "GET",
    });
  },

  /**
   * Fetches JSON Schema specification for a specific response type.
   */
  async getSchemaSpec(schemaType: string): Promise<Record<string, unknown>> {
    return apiClient<Record<string, unknown>>(`/api/v1/rg-ai/schemas/${schemaType}`, {
      method: "GET",
    });
  },

  /**
   * Validates raw text payload against backend schema registry.
   */
  async validateResponse(
    rawResponse: string,
    expectedType?: string,
    requestId?: string
  ): Promise<ResponseEnvelope | ValidationErrorEnvelope> {
    return apiClient<ResponseEnvelope | ValidationErrorEnvelope>(
      "/api/v1/rg-ai/validate-response",
      {
        method: "POST",
        body: JSON.stringify({
          raw_response: rawResponse,
          expected_type: expectedType,
          request_id: requestId,
        }),
      }
    );
  },
};
