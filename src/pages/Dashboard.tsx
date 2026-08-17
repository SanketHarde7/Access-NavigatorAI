/**
 * Dashboard Page
 * ==============
 * Main page showing the live stadium map, stat cards (zones/operational/
 * congested/blocked counts), route planner, demo scenario controls,
 * and zone status grid. This is the primary view of the application.
 */
import { useState, useCallback } from "react";
import { StadiumMap } from "@/components/StadiumMap";
import { RoutePlanner } from "@/components/RoutePlanner";
import { RouteResultCard } from "@/components/RouteResultCard";
import { ZoneStatusGrid } from "@/components/ZoneStatusGrid";
import { CaptionOverlay } from "@/components/CaptionOverlay";
import { DemoControls } from "@/components/DemoControls";
import { GlassCard } from "@/components/GlassCard";
import { useZones } from "@/hooks/useZones";
import { useRoute } from "@/hooks/useRoute";
import { useCaption } from "@/hooks/useCaption";
import { Map, Radio, Activity, Zap } from "lucide-react";

interface DashboardProps {
  stadiumId: string;
}

export function Dashboard({ stadiumId }: DashboardProps) {
  const { zones, lastUpdated, refetch } = useZones(stadiumId);
  const { route, loading: routeLoading, calculateRoute, clearRoute } = useRoute();
  const { caption, clearCaption } = useCaption();

  const [selectedStart, setSelectedStart] = useState("");
  const [selectedEnd, setSelectedEnd] = useState("");
  const [mobileTab, setMobileTab] = useState<"all" | "map" | "planner" | "zones">("all");

  const handleCalculate = useCallback(
    (start: string, end: string, need: string) => {
      calculateRoute(stadiumId, start, end, need);
      // On mobile, switch to map tab to see route if planner tab was active
      if (window.innerWidth < 1024) {
        setMobileTab("map");
      }
    },
    [stadiumId, calculateRoute]
  );

  const handleScenario = useCallback(() => {
    refetch();
    clearRoute();
  }, [refetch, clearRoute]);

  const handleZoneClick = useCallback(
    (zoneId: string) => {
      if (!selectedStart) {
        setSelectedStart(zoneId);
      } else if (!selectedEnd || selectedEnd === zoneId) {
        setSelectedEnd(zoneId);
      } else {
        setSelectedStart(zoneId);
        setSelectedEnd("");
      }
    },
    [selectedStart, selectedEnd]
  );

  return (
    <div className="space-y-3.5 px-3 sm:px-4 pb-4 max-w-7xl mx-auto">
      {/* Mobile Segmented View Switcher */}
      <div className="flex lg:hidden items-center justify-between p-1 bg-black/40 backdrop-blur-md rounded-xl border border-white/10 text-xs">
        {[
          { id: "all", label: "All" },
          { id: "map", label: "Map & Route" },
          { id: "planner", label: "Planner" },
          { id: "zones", label: "Zones" },
        ].map((tab) => {
          const active = mobileTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setMobileTab(tab.id as any)}
              className={`flex-1 py-1.5 px-2 rounded-lg font-medium text-center transition-all ${
                active
                  ? "glass-pill text-white shadow-md"
                  : "text-slate-400 hover:text-slate-200"
              }`}
              style={active ? { color: "var(--theme-accent)" } : undefined}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Top 4 Stat HUD Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 sm:gap-3">
        {[
          { label: "Zones", value: zones.length, icon: <Map className="h-4 w-4" />, iconColor: "#60a5fa" },
          { label: "Operational", value: zones.filter((z) => z.status === "operational").length, icon: <Activity className="h-4 w-4" />, iconColor: "#34d399" },
          { label: "Congested", value: zones.filter((z) => z.status === "congested").length, icon: <Radio className="h-4 w-4" />, iconColor: "#fbbf24" },
          { label: "Blocked", value: zones.filter((z) => z.status === "maintenance").length, icon: <Zap className="h-4 w-4" />, iconColor: "#f87171" },
        ].map((stat) => (
          <GlassCard
            key={stat.label}
            variant="stat"
            tilt
            maxTilt={4}
            className="p-2.5 sm:p-3"
          >
            <div className="flex items-center gap-1.5 sm:gap-2 mb-1">
              <span
                className="p-1 rounded-md"
                style={{
                  background: `${stat.iconColor}22`,
                  color: stat.iconColor,
                  boxShadow: `0 0 8px ${stat.iconColor}66`,
                }}
              >
                {stat.icon}
              </span>
              <span className="text-[9px] sm:text-[10px] text-slate-400 uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className="text-xl sm:text-2xl font-bold text-white">{stat.value}</div>
          </GlassCard>
        ))}
      </div>

      {/* Main Interactive Stage: Left (Map & Route) | Right (Route Planner & Demo) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-3.5 items-start">
        {/* LEFT PANEL (7 cols on desktop): Live Stadium Map */}
        <div className={`lg:col-span-7 space-y-3.5 ${mobileTab === "planner" || mobileTab === "zones" ? "hidden lg:block" : ""}`}>
          <GlassCard tilt maxTilt={3} className="rounded-xl p-3 sm:p-4">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <span
                  className="p-1.5 rounded-lg"
                  style={{
                    background: "var(--theme-bg)",
                    color: "var(--theme-accent)",
                    boxShadow: "0 0 12px var(--theme-glow)",
                  }}
                >
                  <Map className="h-4 w-4" />
                </span>
                Live Stadium Map
              </h2>
              <span className="text-[10px] text-slate-400 glass-pill px-2.5 py-0.5 rounded-full border border-white/10">
                Updated: {lastUpdated.toLocaleTimeString()}
              </span>
            </div>
            <StadiumMap
              zones={zones}
              route={route}
              stadiumId={stadiumId}
              onZoneClick={handleZoneClick}
              selectedStart={selectedStart}
              selectedEnd={selectedEnd}
            />
          </GlassCard>

          <RouteResultCard route={route} />
        </div>

        {/* RIGHT PANEL (5 cols on desktop): Route Planner + Demo Controls */}
        <div className={`lg:col-span-5 space-y-3.5 ${mobileTab === "map" || mobileTab === "zones" ? "hidden lg:block" : ""}`}>
          <GlassCard tilt maxTilt={3} className="rounded-xl p-3 sm:p-4">
            <RoutePlanner
              zones={zones}
              loading={routeLoading}
              onCalculate={handleCalculate}
              selectedStart={selectedStart}
              selectedEnd={selectedEnd}
              onStartChange={setSelectedStart}
              onEndChange={setSelectedEnd}
            />
          </GlassCard>

          <DemoControls stadiumId={stadiumId} onScenarioTriggered={handleScenario} />
        </div>
      </div>

      {/* Zone Status Grid */}
      <div className={`${mobileTab === "map" || mobileTab === "planner" ? "hidden lg:block" : ""}`}>
        <GlassCard tilt={false} className="rounded-xl p-3 sm:p-4">
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <span
              className="p-1.5 rounded-lg"
              style={{
                background: "var(--theme-bg)",
                color: "var(--theme-accent)",
                boxShadow: "0 0 12px var(--theme-glow)",
              }}
            >
              <Activity className="h-4 w-4" />
            </span>
            Zone Status
          </h2>
          <ZoneStatusGrid zones={zones} onZoneClick={handleZoneClick} />
        </GlassCard>
      </div>

      {/* Caption Overlay */}
      <CaptionOverlay caption={caption} onDismiss={clearCaption} />
    </div>
  );
}
