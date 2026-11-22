/**
 * Health check response model from GET /health.
 */

export interface HealthResponse {
  success: boolean;
  application: string;
  status: "healthy" | "degraded" | "unhealthy" | string;
}
