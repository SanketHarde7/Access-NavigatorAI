/**
 * useAnalytics Hook
 * =================
 * Fetches AI-generated stadium analytics including crowd patterns,
 * accessibility compliance scores, and LLM-powered recommendations.
 *
 * @param stadiumId - The stadium to fetch analytics for
 * @returns analytics data, loading/error state, and fetchAnalytics trigger
 */
import { useState, useCallback } from "react";
import { API_ENDPOINTS } from "@/config/api";

/** Analytics data for a single zone. */
export interface ZoneAnalytics {
  zone_id: string;
  avg_crowd_1h: number;
  peak_crowd_1h: number;
  status_changes_1h: number;
  congestion_time_pct: number;
  accessibility_score: number;
}

/** Full analytics response from the /api/analytics endpoint. */
export interface AnalyticsData {
  stadium_id: string;
  generated_at: string;
  total_fans_estimated: number;
  avg_stadium_density: number;
  most_congested_zones: string[];
  accessibility_compliance_score: number;
  zone_analytics: ZoneAnalytics[];
  ai_insights: string[];
  recommendations: string[];
  ai_provider: string;
}

export function useAnalytics(stadiumId: string) {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /** Trigger an analytics fetch from the backend. */
  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(API_ENDPOINTS.analytics(stadiumId));
      if (!res.ok) throw new Error("Failed to fetch analytics");
      const data = await res.json();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [stadiumId]);

  return { analytics, loading, error, fetchAnalytics };
}
