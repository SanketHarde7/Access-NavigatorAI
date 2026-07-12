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
    <header className="sticky top-0 z-50 w-full glass-header">
      <div className="flex h-14 items-center px-4 gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="hover:bg-white/5"
          style={{ color: "var(--theme-accent)" }}
        >
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </Button>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Brain className="h-7 w-7" style={{ color: "var(--theme-accent)" }} />
            <span
              className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full animate-pulse"
              style={{ background: "var(--theme-accent)" }}
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
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full glass-subtle"
          >
            <Activity className="h-3.5 w-3.5" style={{ color: "var(--theme-accent)" }} />
            <span className="text-xs text-slate-300">{stadiumName}</span>
          </div>

          <div className="flex items-center gap-1.5 px-2 py-1 rounded-full glass-subtle">
            {connected ? (
              <Wifi className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <WifiOff className="h-3.5 w-3.5 text-red-400" />
            )}
            <span className={`text-xs ${connected ? "text-emerald-400" : "text-red-400"}`}>
              {connected ? "Live" : "Offline"}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
