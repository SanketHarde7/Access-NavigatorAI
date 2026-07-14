/**
 * useZones Hook
 * =============
 * Fetches and auto-refreshes zone status data for a given stadium.
 * Polls the backend at REFRESH_INTERVAL (default 5s) to keep
 * the Dashboard and StadiumMap up to date with live crowd data.
 *
 * @param stadiumId - The stadium to fetch zones for (e.g. "metlife")
 * @returns zones, loading state, error, lastUpdated timestamp, and refetch fn
 */
import { useState, useEffect, useCallback } from "react";
import { API_ENDPOINTS, REFRESH_INTERVAL } from "@/config/api";

/** Shape of a single zone returned by the /api/zones endpoint. */
export interface Zone {
  zone_id: string;
  type: string;
  status: string;
  crowd_density_pct: number;
  density_trend: string;
  last_updated: string;
  accessibility_score: number;
  elevation_m: number;
  capacity: number;
}

export function useZones(stadiumId: string) {
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchZones = useCallback(async () => {
    try {
      const res = await fetch(API_ENDPOINTS.zones(stadiumId));
      if (!res.ok) throw new Error("Failed to fetch zones");
      const data = await res.json();
      setZones(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }, [stadiumId]);

  useEffect(() => {
    setLoading(true);
    fetchZones();
    const interval = setInterval(fetchZones, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchZones]);

  return { zones, loading, error, lastUpdated, refetch: fetchZones };
}
