/**
 * StadiumMap Component
 * ====================
 * Interactive SVG-based stadium visualization showing:
 * - Zone nodes as colored circles (operational/congested/maintenance)
 * - Connection lines between adjacent zones (from graph data)
 * - Animated route path when a route is calculated
 * - Click-to-select zones for route planning
 * - Crowd density pills on each node
 *
 * Data is fetched from /api/coordinates and /api/graph endpoints.
 * Zone positions are normalized (0–1) and scaled to SVG dimensions.
 */
import { useEffect, useState, useMemo, useCallback } from "react";
import { API_ENDPOINTS } from "@/config/api";
import type { Zone } from "@/hooks/useZones";
import type { RouteResult } from "@/hooks/useRoute";

interface StadiumMapProps {
  /** Array of zone objects with status and crowd data */
  zones: Zone[];
  /** Calculated route result (null if no route) */
  route: RouteResult | null;
  /** Current stadium ID for fetching coordinates/graph */
  stadiumId: string;
  /** Callback when a zone node is clicked */
  onZoneClick?: (zoneId: string) => void;
  /** Currently selected starting zone ID */
  selectedStart?: string;
  /** Currently selected destination zone ID */
  selectedEnd?: string;
}

/** Normalized coordinate (0–1 range) for a zone on the map. */
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

  const scaleCoord = useCallback((c: ZoneCoord) => ({
    x: 50 + c.x * 600,
    y: 50 + c.y * 400
  }), []);

  // Efficiency: memoized SVG geometry keeps live crowd refreshes cheap while preserving the accessibility map semantics.
  const drawConnection = useCallback((fromRaw: ZoneCoord, toRaw: ZoneCoord) => {
    const from = scaleCoord(fromRaw);
    const to = scaleCoord(toRaw);
    const midX = (from.x + to.x) / 2;
    const midY = (from.y + to.y) / 2;
    const cx = svgW / 2 + (midX - svgW / 2) * 0.3;
    const cy = svgH / 2 + (midY - svgH / 2) * 0.3;
    return `M ${from.x} ${from.y} Q ${cx} ${cy} ${to.x} ${to.y}`;
  }, [scaleCoord]);

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
  }, [route, coordinates, drawConnection]);

  return (
    <div>
      <div
        className="relative rounded-xl overflow-hidden glass-3d-subtle"
        style={{ borderColor: "var(--theme-border)" }}
      >
        {/* Grid background */}
        <div className="absolute inset-0 opacity-10">
          <svg width="100%" height="100%">
            <defs>
              <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="currentColor" strokeWidth="0.5" style={{ color: "var(--theme-accent)" }} />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        <svg width={svgW} height={svgH} className="relative z-10 max-w-full h-auto">
          <defs>
            <linearGradient id="zoneGlow" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(255,255,255,0.35)" />
              <stop offset="40%" stopColor="rgba(255,255,255,0.05)" />
              <stop offset="100%" stopColor="rgba(0,0,0,0.4)" />
            </linearGradient>
            <filter id="zoneShadow" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#000" floodOpacity="0.5" />
            </filter>
            <filter id="zoneGlowFilter" x="-50%" y="-50%" width="200%" height="200%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#000" floodOpacity="0.5" />
              <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor="var(--theme-accent)" floodOpacity="0.7" />
            </filter>
          </defs>

          {/* Stadium outline — themed ellipse with depth */}
          <ellipse
            cx={svgW / 2} cy={svgH / 2}
            rx="320" ry="220"
            fill="url(#zoneGlow)" strokeWidth="2"
            style={{ stroke: "var(--theme-border)" }}
            filter="url(#zoneShadow)"
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
                  fill="none" stroke="rgba(148,163,184,0.15)" strokeWidth="1" strokeDasharray="4,4" opacity="0.6"
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
              style={{ stroke: "var(--theme-accent)", filter: "drop-shadow(0 0 6px var(--theme-glow-strong))" }}
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
            const r = isRoute ? 12 : 8;

            return (
              <g
                key={zone.zone_id}
                onClick={() => onZoneClick?.(zone.zone_id)}
                className="cursor-pointer transition-transform hover:scale-110"
                style={{ transformOrigin: `${px}px ${py}px` }}
              >
                {/* Node circle */}
                <circle
                  cx={px} cy={py} r={r}
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  filter={isRoute ? "url(#zoneGlowFilter)" : "drop-shadow(0 2px 4px rgba(0,0,0,0.5))"}
                />
                
                {/* Start / End indicators */}
                {isStart && <circle cx={px} cy={py} r={r - 3} fill="#10b981" />}
                {isEnd && <circle cx={px} cy={py} r={r - 3} fill="#ef4444" />}

                {/* Text Label Below Node */}
                {words.map((word, i) => (
                  <text
                    key={i}
                    x={px}
                    y={py + r + 12 + (i * 10)}
                    textAnchor="middle"
                    className="pointer-events-none select-none capitalize"
                    style={{ fontSize: "9px", fontWeight: "600", fill: "#f1f5f9", textShadow: "0 1px 3px rgba(0,0,0,0.9)" }}
                  >
                    {word}
                  </text>
                ))}

                {/* Crowd Density Pill */}
                {zone.crowd_density_pct > 0 && (
                  <g>
                    <rect
                      x={px - 14}
                      y={py + r + 12 + (words.length * 10)}
                      width="28"
                      height="12"
                      rx="4"
                      fill="rgba(15, 23, 42, 0.8)"
                      stroke={strokeColor}
                      strokeWidth="0.5"
                    />
                    <text
                      x={px}
                      y={py + r + 18 + (words.length * 10)}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="pointer-events-none select-none"
                      style={{ fontSize: "8px", fill: strokeColor, fontWeight: "700" }}
                    >
                      {zone.crowd_density_pct}%
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-3 text-xs text-slate-400">
        {[
          { color: "#10b981", label: "Operational" },
          { color: "#f59e0b", label: "Congested" },
          { color: "#ef4444", label: "Maintenance" },
          { label: "Active Route", useTheme: true },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-1.5 glass-pill px-2 py-1 rounded-full">
            <div
              className="w-2.5 h-2.5 rounded-sm"
              style={{
                background: item.useTheme ? "var(--theme-accent)" : item.color,
                boxShadow: `0 0 6px ${item.useTheme ? "var(--theme-glow-strong)" : item.color}`,
              }}
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
