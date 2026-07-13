import { useState } from "react";
import { Brain, Loader2, Sparkles, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { GlassCard } from "@/components/GlassCard";
import type { PredictionData } from "@/hooks/usePredictions";

interface PredictionPanelProps {
  predictions: PredictionData | null;
  loading: boolean;
  onPredict: (horizon: number) => void;
}

export function PredictionPanel({ predictions, loading, onPredict }: PredictionPanelProps) {
  const [horizon, setHorizon] = useState(30);

  if (loading) {
    return (
      <GlassCard tilt={false} className="rounded-xl p-8 flex flex-col items-center justify-center gap-3">
        <Loader2 className="h-8 w-8 text-violet-400 animate-spin" />
        <p className="text-sm text-slate-400">AI predicting crowd patterns...</p>
      </GlassCard>
    );
  }

  if (!predictions) {
    return (
      <GlassCard tilt maxTilt={4} className="rounded-xl p-8 flex flex-col items-center justify-center gap-4">
        <div
          className="p-3 rounded-xl glass-3d-subtle animate-float"
          style={{ boxShadow: "0 0 25px #a78bfa66" }}
        >
          <Brain className="h-8 w-8 text-violet-400" />
        </div>
        <div className="text-center">
          <h4 className="text-sm font-medium text-slate-300 mb-1">AI Crowd Predictions</h4>
          <p className="text-xs text-slate-500 max-w-[280px]">
            Use AI to predict future crowd density and get proactive recommendations.
          </p>
        </div>
        <div className="w-full max-w-[280px] space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="flex items-center gap-1.5"><Clock className="h-3.5 w-3.5" /> Horizon</span>
            <span>{horizon} min</span>
          </div>
          <Slider value={[horizon]} onValueChange={(v) => setHorizon(v[0])} min={5} max={120} step={5} />
          <Button
            onClick={() => onPredict(horizon)}
            className="w-full btn-theme rounded-xl"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Generate Predictions
          </Button>
        </div>
      </GlassCard>
    );
  }

  const riskColor = predictions.overall_risk === "critical" ? "text-red-400" :
    predictions.overall_risk === "high" ? "text-orange-400" :
    predictions.overall_risk === "medium" ? "text-amber-400" : "text-emerald-400";

  return (
    <GlassCard tilt maxTilt={3} className="rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span
            className="p-1.5 rounded-lg"
            style={{ background: "#a78bfa22", color: "#a78bfa", boxShadow: "0 0 12px #a78bfa66" }}
          >
            <Brain className="h-4 w-4" />
          </span>
          <div>
            <h3 className="text-sm font-semibold text-white">AI Predictions</h3>
            <p className="text-[10px] text-slate-400">via Predictive Agent</p>
          </div>
        </div>
        <div className={`text-xs font-medium ${riskColor} capitalize glass-pill px-2 py-1 rounded-full`}>
          {predictions.overall_risk} Risk
        </div>
      </div>

      <div className="px-4 py-3">
        <p className="text-xs text-slate-300 mb-3">{predictions.summary}</p>

        <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
          {predictions.predictions.map((p) => (
            <div key={p.zone_id} className="flex items-center gap-3 p-2 rounded-lg glass-3d-subtle">
              <span className="text-xs text-slate-300 capitalize w-28 truncate">{p.zone_id.replace(/_/g, " ")}</span>
              <div className="flex-1">
                <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                  <span>{p.predicted_density}% predicted</span>
                  <span className="capitalize">{p.trend_direction}</span>
                </div>
                <div className="h-1.5 bg-black/40 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      p.predicted_density > 85 ? "bg-red-500" :
                      p.predicted_density > 60 ? "bg-amber-500" : "bg-emerald-500"
                    }`}
                    style={{ width: `${p.predicted_density}%`, boxShadow: "0 0 8px currentColor" }}
                  />
                </div>
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded-full glass-pill ${
                p.risk_level === "critical" ? "text-red-400" :
                p.risk_level === "high" ? "text-orange-400" :
                p.risk_level === "medium" ? "text-amber-400" :
                "text-emerald-400"
              }`}>
                {p.risk_level}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="px-4 py-2.5 border-t border-white/5 flex items-center justify-between">
        <span className="text-[10px] text-slate-500">via {predictions.ai_provider}</span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPredict(horizon)}
          className="h-7 text-xs glass-3d-subtle hover:bg-white/10 transition-transform active:scale-95"
        >
          Refresh
        </Button>
      </div>
    </GlassCard>
  );
}
