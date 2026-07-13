import { Activity, TrendingUp, TrendingDown, Minus, Accessibility, Users, AlertTriangle } from "lucide-react";
import { useTilt } from "@/hooks/useTilt";
import type { Zone } from "@/hooks/useZones";

interface ZoneStatusGridProps {
  zones: Zone[];
  onZoneClick?: (zoneId: string) => void;
}

export function ZoneStatusGrid({ zones, onZoneClick }: ZoneStatusGridProps) {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "operational": return <Activity className="h-3.5 w-3.5 text-emerald-400" />;
      case "congested": return <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />;
      case "maintenance": return <AlertTriangle className="h-3.5 w-3.5 text-red-400" />;
      default: return <Minus className="h-3.5 w-3.5 text-slate-500" />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "rising": return <TrendingUp className="h-3 w-3 text-red-400" />;
      case "falling": return <TrendingDown className="h-3 w-3 text-emerald-400" />;
      default: return <Minus className="h-3 w-3 text-slate-500" />;
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
      {zones.map((zone) => (
        <ZoneTile
          key={zone.zone_id}
          zone={zone}
          onClick={() => onZoneClick?.(zone.zone_id)}
          getStatusIcon={getStatusIcon}
          getTrendIcon={getTrendIcon}
        />
      ))}
    </div>
  );
}

interface ZoneTileProps {
  zone: Zone;
  onClick: () => void;
  getStatusIcon: (s: string) => React.ReactNode;
  getTrendIcon: (t: string) => React.ReactNode;
}

function ZoneTile({ zone, onClick, getStatusIcon, getTrendIcon }: ZoneTileProps) {
  const tilt = useTilt<HTMLButtonElement>(6);
  return (
    <button
      ref={tilt.ref as React.RefObject<HTMLButtonElement>}
      onMouseMove={tilt.onMouseMove as (e: React.MouseEvent<HTMLButtonElement>) => void}
      onMouseLeave={tilt.onMouseLeave}
      onClick={onClick}
      className="glass-3d-subtle glass-tilt text-left p-3 rounded-xl transition-all hover:border-white/20"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          {getStatusIcon(zone.status)}
          <span className="text-xs font-medium text-slate-200 capitalize">
            {zone.zone_id.replace(/_/g, " ")}
          </span>
        </div>
        <span className="text-[10px] text-slate-500 capitalize glass-pill px-1.5 py-0.5 rounded">{zone.type}</span>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex-1">
          <div className="flex justify-between text-[10px] text-slate-400 mb-1">
            <span className="flex items-center gap-1">
              <Users className="h-3 w-3" />
              Density
            </span>
            <span className="flex items-center gap-1">
              {zone.crowd_density_pct}%
              {getTrendIcon(zone.density_trend)}
            </span>
          </div>
          <div className="h-1.5 bg-black/40 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                zone.crowd_density_pct > 80 ? "bg-red-500" :
                zone.crowd_density_pct > 60 ? "bg-amber-500" : "bg-emerald-500"
              }`}
              style={{ width: `${zone.crowd_density_pct}%`, boxShadow: "0 0 6px currentColor" }}
            />
          </div>
        </div>

        <div
          className="flex items-center gap-1 px-1.5 py-0.5 rounded glass-pill"
          style={{ color: "var(--theme-accent)" }}
        >
          <Accessibility className="h-3 w-3" />
          <span className="text-[10px] font-medium">
            {Math.round((zone.accessibility_score || 0) * 100)}
          </span>
        </div>
      </div>
    </button>
  );
}
