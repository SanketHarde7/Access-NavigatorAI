import { AlertTriangle, Info, Bell, X } from "lucide-react";
import type { Caption } from "@/hooks/useCaption";

interface CaptionOverlayProps {
  caption: Caption | null;
  onDismiss: () => void;
}

export function CaptionOverlay({ caption, onDismiss }: CaptionOverlayProps) {
  if (!caption) return null;

  const styles = {
    highlighted_red_banner: {
      bg: "linear-gradient(135deg, rgba(239,68,68,0.35), rgba(120,10,10,0.55))",
      borderColor: "rgba(239, 68, 68, 0.6)",
      icon: <AlertTriangle className="h-5 w-5 text-red-300 animate-pulse" />,
      text: "text-red-50",
      glow: "rgba(239, 68, 68, 0.6)",
      pulse: true,
    },
    highlighted: {
      bg: "linear-gradient(135deg, rgba(245,158,11,0.3), rgba(120,80,5,0.55))",
      borderColor: "rgba(245, 158, 11, 0.55)",
      icon: <Bell className="h-5 w-5 text-amber-300" />,
      text: "text-amber-50",
      glow: "rgba(245, 158, 11, 0.55)",
      pulse: false,
    },
    standard: {
      bg: "linear-gradient(135deg, rgba(30,41,59,0.6), rgba(10,15,30,0.75))",
      borderColor: "rgba(148, 163, 184, 0.4)",
      icon: <Info className="h-5 w-5 text-blue-300" />,
      text: "text-slate-50",
      glow: "rgba(59, 130, 246, 0.4)",
      pulse: false,
    },
  };

  const style = styles[caption.style as keyof typeof styles] || styles.standard;

  return (
    <div
      className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-2xl rounded-2xl backdrop-blur-2xl animate-in slide-in-from-bottom-6 duration-300 ${
        style.pulse ? "animate-pulse" : ""
      }`}
      style={{
        background: style.bg,
        border: `1px solid ${style.borderColor}`,
        borderTopColor: "rgba(255, 255, 255, 0.25)",
        boxShadow: `0 40px 80px -10px rgba(0,0,0,0.9), 0 0 60px ${style.glow}, inset 0 1px 0 0 rgba(255,255,255,0.25), inset 0 -1px 8px 0 rgba(0,0,0,0.4)`,
      }}
      role="alert"
      aria-live={caption.urgency === "critical" ? "assertive" : "polite"}
    >
      <button onClick={onDismiss} className="w-full p-4 flex items-center gap-3 text-left">
        <span className="shrink-0">{style.icon}</span>
        <p className={`text-sm font-semibold ${style.text} flex-1`}>{caption.display_text}</p>
        <span className="text-[10px] uppercase tracking-wider text-slate-300 glass-pill px-2 py-0.5 rounded-full">
          {caption.urgency}
        </span>
        <X className="h-4 w-4 text-slate-400 hover:text-white transition-colors shrink-0" />
      </button>
    </div>
  );
}
