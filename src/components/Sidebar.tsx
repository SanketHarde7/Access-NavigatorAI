/**
 * Sidebar Component
 * =================
 * Fixed left sidebar providing:
 * - Stadium selector (MetLife / SoFi / Azteca)
 * - Page navigation (Dashboard / AI Assistant / Analytics)
 * - AI Agent status indicators (Perception, Reasoning, Communication, Navigator)
 * - System health status footer
 *
 * The sidebar uses glassmorphic styling and adapts accent colors
 * to the currently selected stadium theme.
 */
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
  X,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

/** Available pages in the application. */
export type Page = "dashboard" | "navigator" | "chat" | "analytics" | "settings";

interface SidebarProps {
  /** Whether the sidebar is visible */
  open: boolean;
  /** Currently active page */
  currentPage: Page;
  /** Callback when user selects a different page */
  onPageChange: (page: Page) => void;
  /** Currently selected stadium ID */
  stadiumId: string;
  /** Callback when user selects a different stadium */
  onStadiumChange: (id: string) => void;
  /** Optional callback to close the sidebar on mobile */
  onClose?: () => void;
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
  { id: "narendra_modi", name: "Narendra Modi Stadium", location: "Ahmedabad, Gujarat", tag: "132K", color: "#ff5e00" },
  { id: "wankhede", name: "Wankhede Stadium", location: "Mumbai, Maharashtra", tag: "33K", color: "#00e5ff" },
  { id: "chinnaswamy", name: "M. Chinnaswamy Stadium", location: "Bengaluru, Karnataka", tag: "40K", color: "#f43f5e" },
  { id: "eden_gardens", name: "Eden Gardens", location: "Kolkata, West Bengal", tag: "68K", color: "#10b981" },
  { id: "arun_jaitley", name: "Arun Jaitley Stadium", location: "New Delhi, Delhi", tag: "42K", color: "#c084fc" },
];

export function Sidebar({ open, currentPage, onPageChange, stadiumId, onStadiumChange, onClose }: SidebarProps) {
  const handlePageSelect = (page: Page) => {
    onPageChange(page);
    if (window.innerWidth < 1024 && onClose) {
      onClose();
    }
  };

  const handleStadiumSelect = (id: string) => {
    onStadiumChange(id);
    if (window.innerWidth < 1024 && onClose) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {open && (
        <div
          className="fixed inset-0 bg-black/75 backdrop-blur-sm z-40 lg:hidden transition-opacity"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar: Static column on desktop, rich drawer on mobile */}
      <aside
        className={`${
          open ? "flex" : "hidden"
        } fixed lg:static left-0 top-0 bottom-0 z-50 lg:z-auto w-80 max-w-[85vw] lg:w-64 h-full shrink-0 bg-[#060a1c]/95 lg:bg-transparent backdrop-blur-2xl lg:backdrop-blur-none glass-3d-subtle border-r border-white/15 flex-col transition-all duration-300 shadow-2xl lg:shadow-none`}
      >
        {/* Top Header with Close Button on Mobile */}
        <div className="flex items-center justify-between p-4 border-b border-white/10 shrink-0">
          <div className="flex items-center gap-2">
            <div
              className="h-2.5 w-2.5 rounded-full animate-ping"
              style={{ background: "var(--theme-accent)" }}
            />
            <span className="text-xs font-semibold tracking-wider text-slate-300 uppercase">
              Stadium Hub
            </span>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Close sidebar"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <ScrollArea className="flex-1 py-4 min-h-0">
          {/* Stadium Selector */}
          <div className="px-4 mb-2">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2.5 flex items-center justify-between">
              <span>Premier Stadiums</span>
              <span className="text-[10px] text-amber-400 font-normal">5 Venues</span>
            </label>
            <div className="space-y-2">
              {stadiums.map((s) => {
                const active = stadiumId === s.id;
                return (
                  <button
                    key={s.id}
                    onClick={() => handleStadiumSelect(s.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-300 group relative overflow-hidden ${
                      active
                        ? "glass-3d-subtle glow-ring"
                        : "hover:bg-white/5 border border-transparent hover:border-white/10"
                    }`}
                    style={
                      active
                        ? {
                            borderColor: "var(--theme-border)",
                            boxShadow: `0 0 16px var(--theme-glow)`,
                          }
                        : undefined
                    }
                  >
                    <span
                      className="shrink-0 p-1.5 rounded-lg transition-transform group-hover:scale-110 flex items-center justify-center"
                      style={{
                        background: active ? "var(--theme-bg)" : `${s.color}18`,
                        border: `1px solid ${active ? "var(--theme-accent)" : `${s.color}33`}`,
                      }}
                    >
                      <Landmark
                        className="h-4 w-4"
                        style={{ color: active ? "var(--theme-accent)" : s.color }}
                      />
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-1">
                        <span
                          className="text-xs font-semibold truncate"
                          style={{ color: active ? "var(--theme-accent)" : "#f1f5f9" }}
                        >
                          {s.name}
                        </span>
                        <span
                          className="text-[9px] font-bold px-1.5 py-0.5 rounded-md shrink-0"
                          style={{
                            background: active ? "var(--theme-bg)" : "rgba(255,255,255,0.06)",
                            color: active ? "var(--theme-accent)" : "#94a3b8",
                            border: `1px solid ${active ? "var(--theme-border)" : "rgba(255,255,255,0.08)"}`,
                          }}
                        >
                          {s.tag}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-400 truncate mt-0.5">{s.location}</div>
                    </div>
                    {active && (
                      <ChevronRight
                        className="h-4 w-4 shrink-0 animate-pulse ml-0.5"
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
                  onClick={() => handlePageSelect(item.page)}
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
    </>
  );
}
