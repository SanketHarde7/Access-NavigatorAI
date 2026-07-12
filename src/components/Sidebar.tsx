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
    <aside className="fixed left-0 top-14 bottom-0 z-40 w-64 glass-sidebar flex flex-col">
      <ScrollArea className="flex-1 py-4">
        {/* Stadium Selector */}
        <div className="px-4 mb-4">
          <label className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 block">
            Stadium
          </label>
          <div className="space-y-1">
            {stadiums.map((s) => (
              <button
                key={s.id}
                onClick={() => onStadiumChange(s.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all ${
                  stadiumId === s.id
                    ? "glass-card"
                    : "hover:bg-white/5 border border-transparent"
                }`}
                style={stadiumId === s.id ? {
                  borderColor: "var(--theme-border)",
                  boxShadow: `0 0 15px var(--theme-glow)`,
                } : undefined}
              >
                <Landmark
                  className="h-4 w-4"
                  style={{ color: stadiumId === s.id ? "var(--theme-accent)" : "#64748b" }}
                />
                <div>
                  <div
                    className="text-sm font-medium"
                    style={{ color: stadiumId === s.id ? "var(--theme-accent)" : "#cbd5e1" }}
                  >
                    {s.name}
                  </div>
                  <div className="text-[10px] text-slate-500">{s.location}</div>
                </div>
                {stadiumId === s.id && (
                  <ChevronRight className="h-4 w-4 ml-auto" style={{ color: "var(--theme-accent)" }} />
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="mx-4 my-4 h-px bg-white/5" />

        {/* Navigation */}
        <div className="px-4">
          <label className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 block">
            Navigation
          </label>
          <div className="space-y-1">
            {navItems.map((item) => (
              <button
                key={item.page}
                onClick={() => onPageChange(item.page)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all group ${
                  currentPage === item.page
                    ? "glass-subtle"
                    : "hover:bg-white/5 border border-transparent"
                }`}
                style={currentPage === item.page ? {
                  borderColor: "var(--theme-border)",
                } : undefined}
              >
                <span style={{ color: currentPage === item.page ? "var(--theme-accent)" : undefined }}
                      className={currentPage !== item.page ? "text-slate-500 group-hover:text-slate-300" : ""}
                >
                  {item.icon}
                </span>
                <span
                  className={`text-sm font-medium ${
                    currentPage === item.page ? "text-white" : "text-slate-400 group-hover:text-slate-200"
                  }`}
                >
                  {item.label}
                </span>
                {currentPage === item.page && (
                  <div
                    className="ml-auto h-1.5 w-1.5 rounded-full"
                    style={{ background: "var(--theme-accent)" }}
                  />
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="mx-4 my-4 h-px bg-white/5" />

        {/* AI Agents Status */}
        <div className="px-4">
          <label className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-2 block">
            AI Agents
          </label>
          <div className="space-y-2">
            {[
              { name: "Perception", icon: <Brain className="h-3.5 w-3.5" />, color: "text-emerald-400" },
              { name: "Reasoning", icon: <Brain className="h-3.5 w-3.5" />, color: "text-violet-400" },
              { name: "Communication", icon: <Volume2 className="h-3.5 w-3.5" />, color: "text-blue-400" },
              { name: "Navigator", icon: <Navigation className="h-3.5 w-3.5" />, color: "text-amber-400" },
            ].map((agent) => (
              <div
                key={agent.name}
                className="flex items-center gap-2 px-3 py-2 rounded-lg glass-subtle"
              >
                <span className={agent.color}>{agent.icon}</span>
                <span className="text-xs text-slate-300">{agent.name}</span>
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </div>
            ))}
          </div>
        </div>
      </ScrollArea>

      {/* Bottom Status */}
      <div className="p-4 border-t border-white/5">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Shield className="h-3.5 w-3.5 text-emerald-400" />
          <span>All systems operational</span>
        </div>
      </div>
    </aside>
  );
}
