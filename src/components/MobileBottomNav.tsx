/**
 * MobileBottomNav Component
 * =========================
 * Bottom navigation bar displayed exclusively on mobile devices (< lg breakpoint).
 * Provides thumb-friendly navigation tabs for:
 * - Map / Dashboard
 * - AI Assistant
 * - Analytics
 * - Quick Stadium Selector Drawer
 */
import { Map, MessageSquare, BarChart3, Landmark } from "lucide-react";
import type { Page } from "@/components/Sidebar";

interface MobileBottomNavProps {
  currentPage: Page;
  onPageChange: (page: Page) => void;
  onOpenStadiums: () => void;
  stadiumName: string;
}

export function MobileBottomNav({
  currentPage,
  onPageChange,
  onOpenStadiums,
  stadiumName,
}: MobileBottomNavProps) {
  const tabs = [
    {
      id: "dashboard" as Page,
      label: "Map",
      icon: Map,
    },
    {
      id: "chat" as Page,
      label: "AI Assist",
      icon: MessageSquare,
    },
    {
      id: "analytics" as Page,
      label: "Analytics",
      icon: BarChart3,
    },
  ];

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 lg:hidden glass-3d-header border-t border-white/10 pb-[env(safe-area-inset-bottom)]"
      aria-label="Mobile Navigation"
    >
      <div className="flex items-center justify-around px-2 py-1.5 h-16">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentPage === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onPageChange(tab.id)}
              className={`flex-1 flex flex-col items-center justify-center py-1 px-2 rounded-xl transition-all duration-200 active:scale-95 ${
                isActive
                  ? "text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <div
                className={`relative p-1.5 rounded-lg transition-all ${
                  isActive ? "glass-pill" : ""
                }`}
                style={
                  isActive
                    ? {
                        color: "var(--theme-accent)",
                        boxShadow: "0 0 12px var(--theme-glow)",
                      }
                    : undefined
                }
              >
                <Icon className="h-5 w-5" />
                {isActive && (
                  <span
                    className="absolute -top-0.5 -right-0.5 h-1.5 w-1.5 rounded-full animate-pulse"
                    style={{ background: "var(--theme-accent)" }}
                  />
                )}
              </div>
              <span
                className={`text-[11px] font-medium mt-0.5 ${
                  isActive ? "font-semibold text-white" : ""
                }`}
                style={isActive ? { color: "var(--theme-accent)" } : undefined}
              >
                {tab.label}
              </span>
            </button>
          );
        })}

        {/* Quick Stadium Selector button */}
        <button
          onClick={onOpenStadiums}
          className="flex-1 flex flex-col items-center justify-center py-1 px-2 rounded-xl text-slate-400 hover:text-slate-200 transition-all duration-200 active:scale-95"
        >
          <div className="p-1.5 rounded-lg">
            <Landmark className="h-5 w-5 text-slate-300" />
          </div>
          <span className="text-[11px] font-medium mt-0.5 text-slate-300 truncate max-w-[64px]">
            {stadiumName.split(" ")[0]}
          </span>
        </button>
      </div>
    </nav>
  );
}
