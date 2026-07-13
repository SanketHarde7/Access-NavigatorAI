import { BarChart3, Users, AlertTriangle, Sparkles, Loader2, TrendingUp, Shield, Brain } from "lucide-react";
import { GlassCard } from "@/components/GlassCard";
import type { AnalyticsData } from "@/hooks/useAnalytics";

interface AnalyticsPanelProps {
  analytics: AnalyticsData | null;
  loading: boolean;
}

export function AnalyticsPanel({ analytics, loading }: AnalyticsPanelProps) {
  if (loading) {
    return (
      <GlassCard tilt={false} className="rounded-xl p-12 flex flex-col items-center justify-center gap-3">
        <Loader2 className="h-8 w-8 text-cyan-400 animate-spin" />
        <p className="text-sm text-slate-400">AI analyzing stadium data...</p>
      </GlassCard>
    );
  }

  if (!analytics) return null;

  const metrics = [
    {
      label: "Est. Fans",
      value: analytics.total_fans_estimated.toLocaleString(),
      icon: <Users className="h-4 w-4" />,
      color: "#22d3ee",
    },
    {
      label: "Avg Density",
      value: `${analytics.avg_stadium_density}%`,
      icon: <TrendingUp className="h-4 w-4" />,
      color: "#fbbf24",
    },
    {
      label: "Compliance",
      value: `${analytics.accessibility_compliance_score}%`,
      icon: <Shield className="h-4 w-4" />,
      color: "#34d399",
    },
    {
      label: "Congested",
      value: `${analytics.most_congested_zones.length}`,
      icon: <AlertTriangle className="h-4 w-4" />,
      color: "#f87171",
    },
  ];

  return (
    <div className="space-y-4">
      {/* Key Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {metrics.map((metric) => (
          <GlassCard key={metric.label} variant="stat" tilt maxTilt={5} className="p-3">
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className="p-1 rounded-md"
                style={{
                  background: `${metric.color}22`,
                  color: metric.color,
                  boxShadow: `0 0 8px ${metric.color}66`,
                }}
              >
                {metric.icon}
              </span>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">{metric.label}</span>
            </div>
            <div className="text-xl font-bold text-white">{metric.value}</div>
          </GlassCard>
        ))}
      </div>

      {/* AI Insights */}
      {analytics.ai_insights.length > 0 && (
        <GlassCard tilt maxTilt={2} className="rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <span
              className="p-1.5 rounded-lg"
              style={{ background: "#a78bfa22", color: "#a78bfa", boxShadow: "0 0 10px #a78bfa66" }}
            >
              <Brain className="h-4 w-4" />
            </span>
            <h4 className="text-sm font-semibold text-violet-300">AI Insights</h4>
          </div>
          <ul className="space-y-2">
            {analytics.ai_insights.map((insight, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-300">
                <Sparkles className="h-3.5 w-3.5 text-violet-400 mt-0.5 shrink-0" />
                {insight}
              </li>
            ))}
          </ul>
        </GlassCard>
      )}

      {/* Recommendations */}
      {analytics.recommendations.length > 0 && (
        <GlassCard tilt maxTilt={2} className="rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <span
              className="p-1.5 rounded-lg"
              style={{ background: "#34d39922", color: "#34d399", boxShadow: "0 0 10px #34d39966" }}
            >
              <Shield className="h-4 w-4" />
            </span>
            <h4 className="text-sm font-semibold text-emerald-300">AI Recommendations</h4>
          </div>
          <ul className="space-y-2">
            {analytics.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-300">
                <span className="h-4 w-4 rounded-full bg-emerald-900/50 border border-emerald-700/50 flex items-center justify-center text-[10px] text-emerald-400 shrink-0">
                  {i + 1}
                </span>
                {rec}
              </li>
            ))}
          </ul>
        </GlassCard>
      )}

      {/* Zone Analytics Table */}
      <GlassCard tilt={false} className="rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-white/5">
          <h4 className="text-sm font-semibold text-white flex items-center gap-2">
            <span
              className="p-1.5 rounded-lg"
              style={{ background: "#22d3ee22", color: "#22d3ee", boxShadow: "0 0 10px #22d3ee66" }}
            >
              <BarChart3 className="h-4 w-4" />
            </span>
            Zone Analytics
          </h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-white/5">
                <th className="px-4 py-2 text-left text-slate-400 font-medium">Zone</th>
                <th className="px-4 py-2 text-center text-slate-400 font-medium">Avg %</th>
                <th className="px-4 py-2 text-center text-slate-400 font-medium">Peak %</th>
                <th className="px-4 py-2 text-center text-slate-400 font-medium">Congestion %</th>
                <th className="px-4 py-2 text-center text-slate-400 font-medium">Accessibility</th>
              </tr>
            </thead>
            <tbody>
              {analytics.zone_analytics.map((z) => (
                <tr key={z.zone_id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                  <td className="px-4 py-2 text-slate-300 capitalize">{z.zone_id.replace(/_/g, " ")}</td>
                  <td className="px-4 py-2 text-center text-slate-400">{z.avg_crowd_1h}%</td>
                  <td className="px-4 py-2 text-center">
                    <span className={z.peak_crowd_1h > 80 ? "text-red-400" : z.peak_crowd_1h > 60 ? "text-amber-400" : "text-emerald-400"}>
                      {z.peak_crowd_1h}%
                    </span>
                  </td>
                  <td className="px-4 py-2 text-center">
                    <span className={z.congestion_time_pct > 50 ? "text-red-400" : z.congestion_time_pct > 20 ? "text-amber-400" : "text-emerald-400"}>
                      {z.congestion_time_pct}%
                    </span>
                  </td>
                  <td className="px-4 py-2 text-center">
                    <div className="flex items-center justify-center gap-1.5">
                      <div className="h-1.5 w-12 bg-black/40 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${z.accessibility_score > 0.8 ? "bg-emerald-500" : z.accessibility_score > 0.5 ? "bg-amber-500" : "bg-red-500"}`}
                          style={{ width: `${z.accessibility_score * 100}%`, boxShadow: "0 0 6px currentColor" }}
                        />
                      </div>
                      <span className="text-slate-400">{Math.round(z.accessibility_score * 100)}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
