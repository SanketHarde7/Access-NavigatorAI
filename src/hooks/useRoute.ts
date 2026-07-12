import { useState, useCallback } from "react";
import { API_ENDPOINTS } from "@/config/api";

export interface PathSegment {
  from_zone: string;
  to_zone: string;
  estimated_time_min: number;
}

export interface RouteResult {
  recommended_path: string[];
  path_segments: PathSegment[];
  eta_minutes: number;
  reasoning: string;
  alternative_considered: string;
  confidence: string;
  accessibility_score: number;
  crowd_alerts: string[];
  agent_trace?: {
    perception_summary: string;
    reasoning_note: string;
    llm_provider: string;
    fallback_used: boolean;
  };
  generated_at: string;
}

export function useRoute() {
  const [route, setRoute] = useState<RouteResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const calculateRoute = useCallback(
    async (
      stadiumId: string,
      start: string,
      end: string,
      accessibilityNeed: string,
      provider?: string
    ) => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();
        if (provider) params.append("provider", provider);

        const res = await fetch(
          `${API_ENDPOINTS.route}?${params.toString()}`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              user_id: "user_001",
              stadium_id: stadiumId,
              accessibility_need: accessibilityNeed,
              current_location: start,
              destination: end,
            }),
          }
        );
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || "Route calculation failed");
        }
        const data = await res.json();
        setRoute(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        setRoute(null);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const clearRoute = useCallback(() => {
    setRoute(null);
    setError(null);
  }, []);

  return { route, loading, error, calculateRoute, clearRoute };
}
