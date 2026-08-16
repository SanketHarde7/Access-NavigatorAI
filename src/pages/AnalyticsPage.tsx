/**
 * AnalyticsPage
 * =============
 * AI-powered analytics dashboard with crowd predictions and
 * comprehensive stadium insights. Features a configurable prediction
 * horizon slider (5–120 min) and on-demand analytics/prediction buttons.
 */
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
    <div className="space-y-4 p-3 sm:p-4 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4">
        <div>
          <h2 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
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
        <div className="flex items-center gap-2 self-start sm:self-auto">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchAnalytics()}
            className="glass-3d-subtle hover:bg-white/10 text-xs transition-transform active:scale-95"
          >
            <Brain className="h-3.5 w-3.5 mr-1.5" />
            Analytics
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchPredictions(horizon)}
            className="glass-3d-subtle hover:bg-white/10 text-xs transition-transform active:scale-95"
          >
            <Sparkles className="h-3.5 w-3.5 mr-1.5" />
            Predictions
          </Button>
        </div>
      </div>

      {/* Controls */}
      <GlassCard tilt maxTilt={2} className="rounded-xl p-3 sm:p-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4">
          <div className="flex items-center justify-between sm:justify-start gap-2">
            <div className="flex items-center gap-2">
              <span
                className="p-1.5 rounded-lg"
                style={{ background: "#a78bfa22", color: "#a78bfa", boxShadow: "0 0 8px #a78bfa66" }}
              >
                <Clock className="h-4 w-4" />
              </span>
              <span className="text-xs sm:text-sm text-slate-300 font-medium">Prediction Horizon</span>
            </div>
            <span
              className="sm:hidden text-xs font-semibold glass-pill px-2.5 py-1 rounded-full text-center"
              style={{ color: "var(--theme-accent)" }}
            >
              {horizon} min
            </span>
          </div>

          <div className="flex-1 w-full flex items-center gap-3">
            <div className="flex-1">
              <Slider value={[horizon]} onValueChange={(v) => setHorizon(v[0])} min={5} max={120} step={5} />
            </div>
            <span
              className="hidden sm:inline-block text-sm font-medium w-16 glass-pill px-2 py-1 rounded-full text-center"
              style={{ color: "var(--theme-accent)" }}
            >
              {horizon} min
            </span>
          </div>

          <Button
            size="sm"
            onClick={() => fetchPredictions(horizon)}
            className="btn-theme rounded-xl w-full sm:w-auto"
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
