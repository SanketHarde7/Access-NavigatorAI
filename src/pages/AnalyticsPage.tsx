import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { PredictionPanel } from "@/components/PredictionPanel";
import { AnalyticsPanel } from "@/components/AnalyticsPanel";
import { GlassCard } from "@/components/GlassCard";
import { usePredictions } from "@/hooks/usePredictions";
import { useAnalytics } from "@/hooks/useAnalytics";
import { Brain, BarChart3, Sparkles, Clock } from "lucide-react";

interface AnalyticsPageProps {
  stadiumId: string;
}

export function AnalyticsPage({ stadiumId }: AnalyticsPageProps) {
  const { predictions, loading: predLoading, fetchPredictions } = usePredictions(stadiumId);
  const { analytics, loading: analyticsLoading, fetchAnalytics } = useAnalytics(stadiumId);
  const [horizon, setHorizon] = useState(30);

  return (
    <div className="space-y-4 p-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <span
              className="p-1.5 rounded-lg"
              style={{
                background: "var(--theme-bg)",
                color: "var(--theme-accent)",
                boxShadow: "0 0 12px var(--theme-glow)",
              }}
            >
              <BarChart3 className="h-5 w-5" />
            </span>
            AI Analytics & Predictions
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Powered by Predictive Agent with LLM forecasting
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchAnalytics()}
            className="glass-3d-subtle hover:bg-white/10 text-xs transition-transform active:scale-95 hover:-translate-y-0.5"
          >
            <Brain className="h-3.5 w-3.5 mr-1.5" />
            Analytics
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchPredictions(horizon)}
            className="glass-3d-subtle hover:bg-white/10 text-xs transition-transform active:scale-95 hover:-translate-y-0.5"
          >
            <Sparkles className="h-3.5 w-3.5 mr-1.5" />
            Predictions
          </Button>
        </div>
      </div>

      {/* Controls */}
      <GlassCard tilt maxTilt={2} className="rounded-xl p-4">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <div className="flex items-center gap-2">
            <span
              className="p-1.5 rounded-lg"
              style={{ background: "#a78bfa22", color: "#a78bfa", boxShadow: "0 0 8px #a78bfa66" }}
            >
              <Clock className="h-4 w-4" />
            </span>
            <span className="text-sm text-slate-300">Prediction Horizon</span>
          </div>
          <div className="flex-1 w-full max-w-xs">
            <Slider value={[horizon]} onValueChange={(v) => setHorizon(v[0])} min={5} max={120} step={5} />
          </div>
          <span
            className="text-sm font-medium w-16 glass-pill px-2 py-1 rounded-full text-center"
            style={{ color: "var(--theme-accent)" }}
          >
            {horizon} min
          </span>
          <Button
            size="sm"
            onClick={() => fetchPredictions(horizon)}
            className="btn-theme rounded-xl"
          >
            <Sparkles className="h-4 w-4 mr-1.5" />
            Predict
          </Button>
        </div>
      </GlassCard>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <PredictionPanel predictions={predictions} loading={predLoading} onPredict={fetchPredictions} />
        <AnalyticsPanel analytics={analytics} loading={analyticsLoading} />
      </div>
    </div>
  );
}
