import { useState, useCallback } from "react";
import { API_ENDPOINTS } from "@/config/api";

export interface Caption {
  display_text: string;
  urgency: string;
  style: string;
  confidence: number;
  original_text?: string;
}

export function useCaption() {
  const [caption, setCaption] = useState<Caption | null>(null);
  const [loading, setLoading] = useState(false);

  const processCaption = useCallback(async (rawText: string, provider?: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (provider) params.append("provider", provider);

      const res = await fetch(`${API_ENDPOINTS.caption}?${params.toString()}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ raw_text: rawText }),
      });
      if (!res.ok) throw new Error("Caption processing failed");
      const data = await res.json();
      setCaption(data);

      // Haptic feedback for critical alerts
      if (data.urgency === "critical" && navigator.vibrate) {
        navigator.vibrate([200, 100, 200, 100, 500]);
      }
    } catch (err) {
      console.error("Caption error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearCaption = useCallback(() => setCaption(null), []);

  return { caption, loading, processCaption, clearCaption };
}
