import { useState, useCallback } from "react";
import { StadiumMap } from "@/components/StadiumMap";
import { RoutePlanner } from "@/components/RoutePlanner";
import { RouteResultCard } from "@/components/RouteResultCard";
import { ZoneStatusGrid } from "@/components/ZoneStatusGrid";
import { CaptionOverlay } from "@/components/CaptionOverlay";
import { DemoControls } from "@/components/DemoControls";
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

  const handleCalculate = useCallback(
    (start: string, end: string, need: string) => {
      calculateRoute(stadiumId, start, end, need);
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
    <div className="space-y-4 p-4">
      {/* Stats Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: "Zones", value: zones.length, icon: <Map className="h-4 w-4" />, iconColor: "#60a5fa" },
          { label: "Operational", value: zones.filter((z) => z.status === "operational").length, icon: <Activity className="h-4 w-4" />, iconColor: "#34d399" },
          { label: "Congested", value: zones.filter((z) => z.status === "congested").length, icon: <Radio className="h-4 w-4" />, iconColor: "#fbbf24" },
          { label: "Blocked", value: zones.filter((z) => z.status === "maintenance").length, icon: <Zap className="h-4 w-4" />, iconColor: "#f87171" },
        ].map((stat) => (
          <div key={stat.label} className="glass-stat p-3 rounded-xl">
            <div className="flex items-center gap-2 mb-1">
              <span style={{ color: stat.iconColor }}>{stat.icon}</span>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider">{stat.label}</span>
            </div>
            <div className="text-2xl font-bold text-white">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Map & Route */}
        <div className="lg:col-span-2 space-y-4">
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-white flex items-center gap-2">
                <Map className="h-4 w-4" style={{ color: "var(--theme-accent)" }} />
                Live Stadium Map
              </h2>
              <span className="text-[10px] text-slate-500">
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
          </div>

          <RouteResultCard route={route} />
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="glass-card rounded-xl p-4">
            <RoutePlanner
              zones={zones}
              loading={routeLoading}
              onCalculate={handleCalculate}
              selectedStart={selectedStart}
              selectedEnd={selectedEnd}
              onStartChange={setSelectedStart}
              onEndChange={setSelectedEnd}
            />
          </div>

          <DemoControls stadiumId={stadiumId} onScenarioTriggered={handleScenario} />
        </div>
      </div>

      {/* Zone Grid */}
      <div className="glass-card rounded-xl p-4">
        <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
          <Activity className="h-4 w-4" style={{ color: "var(--theme-accent)" }} />
          Zone Status
        </h2>
        <ZoneStatusGrid zones={zones} onZoneClick={handleZoneClick} />
      </div>

      {/* Caption */}
      <CaptionOverlay caption={caption} onDismiss={clearCaption} />
    </div>
  );
}
