/**
 * Header Component
 * ================
 * Top navigation bar displaying the app branding, current stadium name,
 * live/offline connection status, and sidebar toggle. Uses glassmorphic
 * styling via the `glass-3d-header` CSS class.
 */
import {
  Brain,
  Menu,
  X,
  Wifi,
  WifiOff,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  /** Whether the backend API is reachable */
  connected: boolean;
  /** Human-readable stadium name to display */
  stadiumName: string;
  /** Callback to toggle the sidebar open/closed */
  onMenuClick: () => void;
  /** Whether the sidebar is currently open */
  sidebarOpen: boolean;
  /** Current stadium ID (used for theme context) */
  stadiumId?: string;
}

export function Header({ connected, stadiumName, onMenuClick, sidebarOpen }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full glass-3d-header">
      <div className="flex h-14 items-center px-3 sm:px-4 gap-2.5 sm:gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="hover:bg-white/5 transition-transform active:scale-95 shrink-0 h-9 w-9"
          style={{ color: "var(--theme-accent)" }}
          aria-label="Toggle menu"
        >
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>

        <div className="flex items-center gap-2.5 min-w-0">
          <div className="relative shrink-0">
            <div
              className="absolute inset-0 rounded-full blur-md"
              style={{ background: "var(--theme-glow-strong)" }}
              aria-hidden
            />
            <Brain
              className="relative h-6 w-6 sm:h-7 sm:w-7"
              style={{ color: "var(--theme-accent)", filter: "drop-shadow(0 0 8px var(--theme-glow-strong))" }}
            />
            <span
              className="absolute -top-0.5 -right-0.5 h-2 w-2 sm:h-2.5 sm:w-2.5 rounded-full animate-pulse"
              style={{
                background: "var(--theme-accent)",
                boxShadow: `0 0 8px var(--theme-glow-strong)`,
              }}
            />
          </div>
          <div className="min-w-0">
            <h1 className="text-sm sm:text-lg font-bold text-white tracking-tight truncate">
              Access Navigator <span className="theme-gradient-text">AI</span>
            </h1>
            <p className="text-[9px] sm:text-[10px] text-slate-400 -mt-0.5 hidden xs:block truncate">
              Accessibility Navigation System
            </p>
          </div>
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          <button
            onClick={onMenuClick}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full glass-pill hover:bg-white/10 transition-all max-w-[120px] sm:max-w-[180px]"
            title="Switch stadium"
          >
            <Activity
              className="h-3.5 w-3.5 shrink-0"
              style={{ color: "var(--theme-accent)" }}
            />
            <span className="text-[11px] sm:text-xs text-slate-200 truncate">
              {stadiumName}
            </span>
          </button>

          <div className="flex items-center gap-1.5 px-2 py-1 rounded-full glass-pill shrink-0">
            {connected ? (
              <Wifi className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <WifiOff className="h-3.5 w-3.5 text-red-400" />
            )}
            <span className={`text-[11px] sm:text-xs font-medium ${connected ? "text-emerald-400" : "text-red-400"}`}>
              {connected ? "Live" : "Offline"}
            </span>
            {connected && (
              <span
                className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse hidden sm:inline-block"
                style={{ boxShadow: "0 0 6px #34d399" }}
              />
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
