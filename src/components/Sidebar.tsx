import {
  Map,
  MessageSquare,
  BarChart3,
  Brain,
  Navigation,
  Volume2,
  Shield,
  ChevronRight,
  Landmark,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

export type Page = "dashboard" | "navigator" | "chat" | "analytics" | "settings";

interface SidebarProps {
  open: boolean;
  currentPage: Page;
  onPageChange: (page: Page) => void;
  stadiumId: string;
  onStadiumChange: (id: string) => void;
}

const navItems: { page: Page; label: string; icon: React.ReactNode }[] = [
  {
    page: "dashboard",
    label: "Dashboard",
    icon: <Map className="h-5 w-5" />,
  },
  {
    page: "chat",
    label: "AI Assistant",
    icon: <MessageSquare className="h-5 w-5" />,
  },
  {
    page: "analytics",
    label: "Analytics",
    icon: <BarChart3 className="h-5 w-5" />,
  },
];

const stadiums = [
  { id: "metlife", name: "MetLife Stadium", location: "East Rutherford, NJ" },
  { id: "sofi", name: "SoFi Stadium", location: "Inglewood, CA" },
  { id: "azteca", name: "Estadio Azteca", location: "Mexico City, MX" },
];

export function Sidebar({ open, currentPage, onPageChange, stadiumId, onStadiumChange }: SidebarProps) {
  if (!open) return null;

  return (
    <aside className="fixed left-0 top-14 bottom-0 z-40 w-64 glass-3d-sidebar flex flex-col">
      <ScrollArea className="flex-1 py-4">
        {/* Stadium Selector */}
        <div className="px-4 mb-4">
          <label className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 block">
            Stadium
          </label>
          <div className="space-y-1.5">
            {stadiums.map((s) => {
              const active = stadiumId === s.id;
              return (
                <button
                  key={s.id}
                  onClick={() => onStadiumChange(s.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-300 group ${
                    active
                      ? "glass-3d-subtle glow-ring"
                      : "hover:bg-white/5 border border-transparent hover:border-white/10"
                  }`}
                  style={
                    active
                      ? {
                          borderColor: "var(--theme-border)",
                        }
                      : undefined
                  }
                >
                  <span
                    className="shrink-0 p-1.5 rounded-lg transition-transform group-hover:scale-110"
                    style={{
                      background: active ? "var(--theme-bg)" : "transparent",
                      boxShadow: active ? `0 0 12px var(--theme-glow)` : "none",
                    }}
                  >
                    <Landmark
                      className="h-4 w-4"
                      style={{ color: active ? "var(--theme-accent)" : "#64748b" }}
                    />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div
                      className="text-sm font-medium truncate"
                      style={{ color: active ? "var(--theme-accent)" : "#cbd5e1" }}
                    >
                      {s.name}
                    </div>
                    <div className="text-[10px] text-slate-500 truncate">{s.location}</div>
                  </div>
                  {active && (
                    <ChevronRight
                      className="h-4 w-4 shrink-0 animate-pulse"
                      style={{ color: "var(--theme-accent)" }}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        <div className="mx-4 my-4 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* Navigation */}
        <div className="px-4">
          <label className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 block">
            Navigation
          </label>
          <div className="space-y-1.5">
            {navItems.map((item) => {
              const active = currentPage === item.page;
              return (
                <button
                  key={item.page}
                  onClick={() => onPageChange(item.page)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-300 group ${
                    active
                      ? "glass-3d-subtle glow-ring"
                      : "hover:bg-white/5 border border-transparent hover:border-white/10"
                  }`}
                  style={
                    active
                      ? {
                          borderColor: "var(--theme-border)",
                        }
                      : undefined
                  }
                >
                  <span
                    className="shrink-0 p-1.5 rounded-lg transition-transform group-hover:scale-110"
                    style={{
                      background: active ? "var(--theme-bg)" : "transparent",
                      boxShadow: active ? `0 0 12px var(--theme-glow)` : "none",
                    }}
                  >
                    <span style={{ color: active ? "var(--theme-accent)" : undefined }}
                          className={active ? "" : "text-slate-500 group-hover:text-slate-300"}>
                      {item.icon}
                    </span>
                  </span>
                  <span
                    className={`text-sm font-medium ${
                      active ? "text-white" : "text-slate-400 group-hover:text-slate-200"
                    }`}
                  >
                    {item.label}
                  </span>
                  {active && (
                    <div
                      className="ml-auto h-1.5 w-1.5 rounded-full animate-pulse"
                      style={{ background: "var(--theme-accent)", boxShadow: `0 0 8px var(--theme-glow-strong)` }}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>

        <div className="mx-4 my-4 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

        {/* AI Agents Status */}
        <div className="px-4">
          <label className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 block">
            AI Agents
          </label>
          <div className="space-y-2">
            {[
              { name: "Perception", icon: <Brain className="h-3.5 w-3.5" />, color: "#34d399" },
              { name: "Reasoning", icon: <Brain className="h-3.5 w-3.5" />, color: "#a78bfa" },
              { name: "Communication", icon: <Volume2 className="h-3.5 w-3.5" />, color: "#60a5fa" },
              { name: "Navigator", icon: <Navigation className="h-3.5 w-3.5" />, color: "#fbbf24" },
            ].map((agent) => (
              <div
                key={agent.name}
                className="flex items-center gap-2.5 px-3 py-2 rounded-xl glass-3d-subtle"
              >
                <span
                  className="shrink-0 p-1 rounded-md"
                  style={{ background: `${agent.color}22`, color: agent.color }}
                >
                  {agent.icon}
                </span>
                <span className="text-xs text-slate-300 flex-1">{agent.name}</span>
                <span
                  className="h-1.5 w-1.5 rounded-full animate-pulse"
                  style={{ background: agent.color, boxShadow: `0 0 6px ${agent.color}` }}
                />
              </div>
            ))}
          </div>
        </div>
      </ScrollArea>

      {/* Bottom Status */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-2 text-xs text-slate-500 glass-3d-subtle px-3 py-2 rounded-xl">
          <Shield className="h-3.5 w-3.5 text-emerald-400" />
          <span>All systems operational</span>
          <span className="ml-auto h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"
                style={{ boxShadow: "0 0 8px #34d399" }} />
        </div>
      </div>
    </aside>
  );
}
