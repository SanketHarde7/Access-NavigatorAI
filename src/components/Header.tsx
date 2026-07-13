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
  connected: boolean;
  stadiumName: string;
  onMenuClick: () => void;
  sidebarOpen: boolean;
  stadiumId?: string;
}

export function Header({ connected, stadiumName, onMenuClick, sidebarOpen }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 w-full glass-3d-header">
      <div className="flex h-14 items-center px-4 gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="hover:bg-white/5 transition-transform active:scale-95"
          style={{ color: "var(--theme-accent)" }}
        >
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>

        <div className="flex items-center gap-3">
          <div className="relative">
            <div
              className="absolute inset-0 rounded-full blur-md"
              style={{ background: "var(--theme-glow-strong)" }}
              aria-hidden
            />
            <Brain
              className="relative h-7 w-7"
              style={{ color: "var(--theme-accent)", filter: "drop-shadow(0 0 8px var(--theme-glow-strong))" }}
            />
            <span
              className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full animate-pulse"
              style={{
                background: "var(--theme-accent)",
                boxShadow: `0 0 8px var(--theme-glow-strong)`,
              }}
            />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">
              Access Navigator <span className="theme-gradient-text">AI</span>
            </h1>
            <p className="text-[10px] text-slate-400 -mt-0.5">Multi-Agent Accessibility System</p>
          </div>
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-3">
          <div
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full glass-pill"
          >
            <Activity
              className="h-3.5 w-3.5"
              style={{ color: "var(--theme-accent)" }}
            />
            <span className="text-xs text-slate-200">{stadiumName}</span>
          </div>

          <div className="flex items-center gap-1.5 px-2 py-1 rounded-full glass-pill">
            {connected ? (
              <Wifi className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <WifiOff className="h-3.5 w-3.5 text-red-400" />
            )}
            <span className={`text-xs ${connected ? "text-emerald-400" : "text-red-400"}`}>
              {connected ? "Live" : "Offline"}
            </span>
            {connected && (
              <span
                className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"
                style={{ boxShadow: "0 0 6px #34d399" }}
              />
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
