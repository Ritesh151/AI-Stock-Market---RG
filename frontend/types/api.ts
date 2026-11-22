/**
 * Standard API Response contracts matching backend envelopes.
 */

export interface ApiErrorDetail {
  field?: string;
  issue: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: ApiErrorDetail[] | null;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
}
