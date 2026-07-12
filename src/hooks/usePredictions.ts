import { useState, useCallback } from "react";
import { API_ENDPOINTS } from "@/config/api";

export interface CrowdPrediction {
  zone_id: string;
  predicted_density: number;
  confidence: number;
  trend_direction: string;
  risk_level: string;
  recommended_action: string;
}

export interface PredictionData {
  predictions: CrowdPrediction[];
  overall_risk: string;
  summary: string;
  stadium_id: string;
  generated_at: string;
  prediction_horizon_min: number;
  ai_provider: string;
}

export function usePredictions(stadiumId: string) {
  const [predictions, setPredictions] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPredictions = useCallback(
    async (horizonMinutes: number = 30) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(
          `${API_ENDPOINTS.predictions(stadiumId)}?horizon_minutes=${horizonMinutes}`
        );
        if (!res.ok) throw new Error("Failed to fetch predictions");
        const data = await res.json();
        setPredictions(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    },
    [stadiumId]
  );

  return { predictions, loading, error, fetchPredictions };
}
