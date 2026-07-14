/**
 * usePredictions Hook
 * ===================
 * Fetches AI-powered crowd density predictions for a given stadium.
 * Uses the PredictionService backend with LLM-based forecasting.
 *
 * @param stadiumId - The stadium to fetch predictions for
 * @returns prediction data, loading/error state, and fetchPredictions trigger
 */
import { useState, useCallback } from "react";
import { API_ENDPOINTS } from "@/config/api";

/** Crowd prediction data for a single zone. */
export interface CrowdPrediction {
  zone_id: string;
  predicted_density: number;
  confidence: number;
  trend_direction: string;
  risk_level: string;
  recommended_action: string;
}

/** Full prediction response from the /api/predictions endpoint. */
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

  /**
   * Fetch crowd predictions for the given horizon.
   * @param horizonMinutes - How far ahead to predict (5–120 min, default 30)
   */
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
