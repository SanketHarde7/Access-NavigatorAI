import { useState } from "react";
import { Clock, MapPin, Brain, ChevronDown, ChevronUp, Shield, AlertTriangle, Sparkles } from "lucide-react";
import { GlassCard } from "@/components/GlassCard";
import type { RouteResult } from "@/hooks/useRoute";

interface RouteResultCardProps {
  route: RouteResult | null;
}

export function RouteResultCard({ route }: RouteResultCardProps) {
  const [showTrace, setShowTrace] = useState(false);
  if (!route) return null;

  const confidenceColor =
    route.confidence === "high" ? "text-emerald-400" : route.confidence === "medium" ? "text-amber-400" : "text-red-400";

  const confidenceBg =
    route.confidence === "high" ? "bg-emerald-950/40" : route.confidence === "medium" ? "bg-amber-950/40" : "bg-red-950/40";

  return (
    <GlassCard tilt maxTilt={3} className="rounded-xl overflow-hidden animate-slide-up">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div
            className="p-1.5 rounded-lg glass-3d-subtle"
            style={{ borderColor: "var(--theme-border)" }}
          >
            <MapPin className="h-4 w-4" style={{ color: "var(--theme-accent)" }} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-white">AI Route Result</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full glass-pill ${confidenceBg} ${confidenceColor} capitalize`}>
                {route.confidence} confidence
              </span>
            </div>
            <p className="text-[10px] text-slate-400">via Reasoning Agent + CoT</p>
          </div>
        </div>
        <div
          className="flex items-center gap-1.5 glass-pill px-2.5 py-1 rounded-full"
          style={{ color: "var(--theme-accent)" }}
        >
          <Clock className="h-4 w-4" />
          <span className="text-sm font-bold">{route.eta_minutes} min</span>
        </div>
      </div>

      {/* Path */}
      <div className="px-4 py-3">
        <div className="flex items-center gap-1.5 flex-wrap">
          {route.recommended_path.map((zone, i) => (
            <div key={zone} className="flex items-center gap-1.5">
              <span className="px-2.5 py-1 rounded-md glass-pill text-xs text-slate-200 capitalize">
                {zone.replace(/_/g, " ")}
              </span>
              {i < route.recommended_path.length - 1 && (
                <div
                  className="w-4 h-px"
                  style={{ background: "var(--theme-accent)", boxShadow: "0 0 4px var(--theme-glow)" }}
                />
              )}
            </div>
          ))}
        </div>

        {/* Accessibility Score */}
        {route.accessibility_score !== undefined && (
          <div className="mt-3 flex items-center gap-3">
            <div className="flex-1">
              <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                <span>Accessibility Score</span>
                <span className={route.accessibility_score > 0.8 ? "text-emerald-400" : route.accessibility_score > 0.5 ? "text-amber-400" : "text-red-400"}>
                  {Math.round(route.accessibility_score * 100)}%
                </span>
              </div>
              <div className="h-2 bg-black/40 rounded-full overflow-hidden shadow-inner">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ${
                    route.accessibility_score > 0.8 ? "bg-emerald-500" : route.accessibility_score > 0.5 ? "bg-amber-500" : "bg-red-500"
                  }`}
                  style={{
                    width: `${route.accessibility_score * 100}%`,
                    boxShadow: "0 0 10px currentColor",
                  }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Reasoning */}
      <div className="px-4 py-3 border-t border-white/5 space-y-2">
        <div className="flex items-start gap-2">
          <Brain className="h-3.5 w-3.5 text-violet-400 mt-0.5 shrink-0" />
          <p className="text-xs text-slate-300 leading-relaxed">{route.reasoning}</p>
        </div>
        {route.alternative_considered && (
          <div className="flex items-start gap-2">
            <Sparkles className="h-3.5 w-3.5 text-amber-400 mt-0.5 shrink-0" />
            <p className="text-xs text-slate-500">{route.alternative_considered}</p>
          </div>
        )}
      </div>

      {/* Alerts */}
      {route.crowd_alerts && route.crowd_alerts.length > 0 && (
        <div className="px-4 py-2.5 border-t border-amber-800/20 bg-amber-950/10">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0" />
            <span className="text-xs text-amber-300">{route.crowd_alerts.join("; ")}</span>
          </div>
        </div>
      )}

      {/* Agent Trace */}
      {route.agent_trace && (
        <div className="border-t border-white/5">
          <button
            onClick={() => setShowTrace(!showTrace)}
            className="w-full px-4 py-2 flex items-center justify-between text-xs text-slate-400 hover:text-slate-300 transition-colors"
          >
            <span className="flex items-center gap-2">
              <Shield className="h-3.5 w-3.5" />
              AI Decision Trace
            </span>
            {showTrace ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
          {showTrace && (
            <div className="px-4 pb-3 space-y-2">
              <div className="p-2.5 rounded-lg glass-3d-subtle">
                <div className="text-[10px] text-emerald-400 font-medium mb-1">Step 1: Perception Agent</div>
                <p className="text-[10px] text-slate-500 line-clamp-3">{route.agent_trace.perception_summary}</p>
              </div>
              <div className="p-2.5 rounded-lg glass-3d-subtle">
                <div className="text-[10px] text-violet-400 font-medium mb-1">Step 2: Reasoning Agent</div>
                <p className="text-[10px] text-slate-500">{route.agent_trace.reasoning_note}</p>
              </div>
              <div className="flex items-center gap-2 text-[10px] text-slate-500">
                <span>Provider: {route.agent_trace.llm_provider}</span>
                {route.agent_trace.fallback_used && (
                  <span className="text-amber-400">(fallback used)</span>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </GlassCard>
  );
}
