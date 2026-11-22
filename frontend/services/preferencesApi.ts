/**
 * User Preferences API Client.
 * Connects frontend UI to MongoDB persistence for user preferences and application settings.
 */

import { apiClient } from "@/services/apiClient";

export interface UserPreferences {
  user_id: string;
  theme: "off-white";
  default_exchange: "NSE" | "BSE";
  preferred_chart_type: "area" | "line" | "candlestick";
  default_chart_range: "1D" | "5D" | "1M" | "3M" | "6M" | "1Y" | "5Y";
  dashboard_preferences?: Record<string, unknown>;
  notification_preferences?: Record<string, unknown>;
  learning_preferences?: Record<string, unknown>;
}

export type UserPreferencesUpdate = Partial<Omit<UserPreferences, "user_id">>;

export const preferencesApi = {
  async get(): Promise<UserPreferences> {
    const res = await apiClient<{ success: boolean; data: UserPreferences }>(
      "/api/v1/preferences"
    );
    return res.data;
  },

  async update(updates: UserPreferencesUpdate): Promise<UserPreferences> {
    const res = await apiClient<{ success: boolean; data: UserPreferences }>(
      "/api/v1/preferences",
      {
        method: "PATCH",
        body: JSON.stringify(updates),
      }
    );
    return res.data;
  },
};
