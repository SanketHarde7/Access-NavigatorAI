import { useEffect, useState, useMemo } from "react";
import { API_ENDPOINTS } from "@/config/api";
import type { Zone } from "@/hooks/useZones";
import type { RouteResult } from "@/hooks/useRoute";

interface StadiumMapProps {
  zones: Zone[];
  route: RouteResult | null;
  stadiumId: string;
  onZoneClick?: (zoneId: string) => void;
  selectedStart?: string;
  selectedEnd?: string;
}

interface ZoneCoord {
  x: number;
  y: number;
}

export function StadiumMap({ zones, route, stadiumId, onZoneClick, selectedStart, selectedEnd }: StadiumMapProps) {
  const [coordinates, setCoordinates] = useState<Record<string, ZoneCoord>>({});
  const [graph, setGraph] = useState<Record<string, Record<string, number>>>({});

  useEffect(() => {
    fetch(API_ENDPOINTS.coordinates(stadiumId))
      .then((r) => r.json())
      .then(setCoordinates)
      .catch(console.error);
    fetch(API_ENDPOINTS.graph(stadiumId))
      .then((r) => r.json())
      .then(setGraph)
      .catch(console.error);
  }, [stadiumId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "operational": return "#10b981";
      case "congested": return "#f59e0b";
      case "maintenance": return "#ef4444";
      case "closed": return "#6b7280";
      default: return "#334155";
    }
  };

  const getStatusFill = (status: string, isRoute: boolean) => {
    if (isRoute) return "rgba(59, 130, 246, 0.15)";
    switch (status) {
      case "operational": return "rgba(16, 185, 129, 0.08)";
      case "congested": return "rgba(245, 158, 11, 0.08)";
      case "maintenance": return "rgba(239, 68, 68, 0.08)";
      default: return "rgba(51, 65, 85, 0.08)";
    }
  };

  const sortedZones = useMemo(() => {
    const order: Record<string, number> = {};
    if (Object.keys(graph).length > 0) {
      const visited = new Set<string>();
      const queue = Object.keys(graph);
      let idx = 0;
      while (queue.length > 0) {
        const current = queue.shift()!;
        if (!visited.has(current)) {
          visited.add(current);
          order[current] = idx++;
          Object.keys(graph[current] || {}).forEach((n) => {
            if (!visited.has(n)) queue.push(n);
          });
        }
      }
      zones.forEach((z) => {
        if (!(z.zone_id in order)) order[z.zone_id] = idx++;
      });
    } else {
      zones.forEach((z, i) => { order[z.zone_id] = i; });
    }
    return [...zones].sort((a, b) => order[a.zone_id] - order[b.zone_id]);
  }, [zones, graph]);

  const svgW = 700;
  const svgH = 500;

  const scaleCoord = (c: ZoneCoord) => ({
    x: 50 + c.x * 600,
    y: 50 + c.y * 400
  });

  const drawConnection = (fromRaw: ZoneCoord, toRaw: ZoneCoord) => {
    const from = scaleCoord(fromRaw);
    const to = scaleCoord(toRaw);
    const midX = (from.x + to.x) / 2;
    const midY = (from.y + to.y) / 2;
    const cx = svgW / 2 + (midX - svgW / 2) * 0.3;
    const cy = svgH / 2 + (midY - svgH / 2) * 0.3;
    return `M ${from.x} ${from.y} Q ${cx} ${cy} ${to.x} ${to.y}`;
  };

  // Route path
  const routePath = useMemo(() => {
    if (!route?.recommended_path || route.recommended_path.length < 2) return "";
    let d = "";
    const path = route.recommended_path;
    for (let i = 0; i < path.length - 1; i++) {
      const from = coordinates[path[i]];
      const to = coordinates[path[i + 1]];
      if (from && to) d += drawConnection(from, to) + " ";
    }
    return d;
  }, [route, coordinates]);

  return (
    <div>
      <div className="relative rounded-xl overflow-hidden glass-subtle" style={{ borderColor: "var(--theme-border)" }}>
        {/* Grid background */}
        <div className="absolute inset-0 opacity-5">
          <svg width="100%" height="100%">
            <defs>
              <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="currentColor" strokeWidth="0.5" style={{ color: "var(--theme-accent)" }} />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        <svg width={svgW} height={svgH} className="relative z-10">
          {/* Stadium outline — themed ellipse */}
          <ellipse
            cx={svgW / 2} cy={svgH / 2}
            rx="320" ry="220"
            fill="none" strokeWidth="2"
            style={{ stroke: "var(--theme-border)" }}
          />
          <ellipse
            cx={svgW / 2} cy={svgH / 2}
            rx="150" ry="90"
            fill="var(--theme-bg)" strokeWidth="1" strokeDasharray="8,4"
            style={{ stroke: "var(--theme-accent)" }}
          />

          {/* Connection lines */}
          {Object.keys(graph).map((fromId) =>
            Object.keys(graph[fromId] || {}).map((toId) => {
              const from = coordinates[fromId];
              const to = coordinates[toId];
              if (!from || !to) return null;
              return (
                <path
                  key={`${fromId}-${toId}`}
                  d={drawConnection(from, to)}
                  fill="none" stroke="rgba(148,163,184,0.1)" strokeWidth="1" strokeDasharray="4,4" opacity="0.5"
                />
              );
            })
          )}

          {/* Route path */}
          {routePath && (
            <path
              d={routePath}
              fill="none" strokeWidth="4" strokeDasharray="8,4"
              className="animate-dash"
              style={{ stroke: "var(--theme-accent)" }}
            />
          )}

          {/* Zone nodes */}
          {sortedZones.map((zone) => {
            const posRaw = coordinates[zone.zone_id];
            if (!posRaw) return null;
            
            const pos = scaleCoord(posRaw);
            const px = pos.x;
            const py = pos.y;

            const isRoute = route?.recommended_path?.includes(zone.zone_id);
            const isStart = zone.zone_id === selectedStart;
            const isEnd = zone.zone_id === selectedEnd;
            const strokeColor = isRoute ? "var(--theme-accent)" : getStatusColor(zone.status);
            const fillColor = getStatusFill(zone.status, !!isRoute);
            const strokeWidth = isRoute ? 3 : isStart || isEnd ? 3 : 1.5;

            const label = zone.zone_id.replace(/_/g, " ");
            const words = label.split(" ");
            const w = 110;
            const h = Math.max(40, words.length * 12 + 16);

            return (
              <g
                key={zone.zone_id}
                onClick={() => onZoneClick?.(zone.zone_id)}
                className="cursor-pointer hover:opacity-90 transition-opacity"
              >
                <rect
                  x={px - w / 2} y={py - h / 2}
                  width={w} height={h}
                  rx="12"
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  style={{ filter: isRoute ? `drop-shadow(0 0 6px var(--theme-glow))` : undefined }}
                />
                {isStart && (
                  <circle cx={px - w / 2 + 8} cy={py - h / 2 + 8} r="5" fill="#10b981" />
                )}
                {isEnd && (
                  <circle cx={px - w / 2 + 8} cy={py - h / 2 + 8} r="5" fill="#ef4444" />
                )}
                {words.map((word, i) => (
                  <text
                    key={i}
                    x={px}
                    y={py - (words.length * 6) + (i * 12) + 4}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="pointer-events-none select-none"
                    style={{ fontSize: "10px", fontWeight: "600", fill: "#e2e8f0" }}
                  >
                    {word}
                  </text>
                ))}
                {zone.crowd_density_pct > 0 && (
                  <text
                    x={px}
                    y={py + (words.length * 6) + 2}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="pointer-events-none select-none"
                    style={{ fontSize: "9px", fill: strokeColor, fontWeight: "500" }}
                  >
                    {zone.crowd_density_pct}%
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-400">
        {[
          { color: "#10b981", label: "Operational" },
          { color: "#f59e0b", label: "Congested" },
          { color: "#ef4444", label: "Maintenance" },
          { label: "Active Route", useTheme: true },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-1.5">
            <div
              className="w-2.5 h-2.5 rounded-sm"
              style={{ background: item.useTheme ? "var(--theme-accent)" : item.color }}
            />
            <span>{item.label}</span>
          </div>
        ))}
      </div>

      <style>{`
        @keyframes dash {
          to { stroke-dashoffset: -200; }
        }
        .animate-dash {
          animation: dash 2s linear infinite;
        }
      `}</style>
    </div>
  );
}
