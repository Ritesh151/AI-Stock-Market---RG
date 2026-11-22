/**
 * Saved Analyses API Client.
 * Connects frontend UI to MongoDB persistence for saved stock intelligence reports.
 */

import { apiClient } from "@/services/apiClient";

export interface SavedAnalysis {
  analysis_id: string;
  user_id: string;
  conversation_id?: string;
  symbol: string;
  exchange: string;
  analysis_type: string;
  validated_data: Record<string, unknown>;
  schema_version: string;
  data_timestamp: string;
  data_source: string;
  created_at: string;
}

export interface SaveAnalysisPayload {
  conversation_id?: string;
  symbol: string;
  exchange?: string;
  analysis_type?: string;
  validated_data: Record<string, unknown>;
  schema_version?: string;
  data_source?: string;
}

export const analysesApi = {
  async list(symbol?: string, analysisType?: string): Promise<SavedAnalysis[]> {
    const params = new URLSearchParams();
    if (symbol) params.set("symbol", symbol);
    if (analysisType) params.set("analysis_type", analysisType);
    const queryString = params.toString() ? `?${params.toString()}` : "";
    const res = await apiClient<{ success: boolean; data: SavedAnalysis[] }>(
      `/api/v1/analyses${queryString}`
    );
    return res?.data || [];
  },

  async get(id: string): Promise<SavedAnalysis | null> {
    const res = await apiClient<{ success: boolean; data: SavedAnalysis }>(
      `/api/v1/analyses/${id}`
    );
    return res?.data || null;
  },

  async save(payload: SaveAnalysisPayload): Promise<SavedAnalysis> {
    const res = await apiClient<{ success: boolean; data: SavedAnalysis }>(
      "/api/v1/analyses",
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
    return res.data;
  },

  async delete(id: string): Promise<boolean> {
    const res = await apiClient<{ success: boolean; data: { deleted: boolean } }>(
      `/api/v1/analyses/${id}`,
      { method: "DELETE" }
    );
    return res?.data?.deleted ?? false;
  },
};
