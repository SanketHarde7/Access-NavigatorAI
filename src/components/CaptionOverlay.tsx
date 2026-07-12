import { AlertTriangle, Info, Bell } from "lucide-react";
import type { Caption } from "@/hooks/useCaption";

interface CaptionOverlayProps {
  caption: Caption | null;
  onDismiss: () => void;
}

export function CaptionOverlay({ caption, onDismiss }: CaptionOverlayProps) {
  if (!caption) return null;

  const styles = {
    highlighted_red_banner: {
      bg: "bg-red-950/90 border-red-500/50",
      icon: <AlertTriangle className="h-5 w-5 text-red-400 animate-pulse" />,
      text: "text-red-100",
      pulse: true,
    },
    highlighted: {
      bg: "bg-amber-950/90 border-amber-500/50",
      icon: <Bell className="h-5 w-5 text-amber-400" />,
      text: "text-amber-100",
      pulse: false,
    },
    standard: {
      bg: "bg-slate-900/95 border-slate-600/50",
      icon: <Info className="h-5 w-5 text-blue-400" />,
      text: "text-slate-100",
      pulse: false,
    },
  };

  const style = styles[caption.style as keyof typeof styles] || styles.standard;

  return (
    <div
      className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-2xl rounded-xl border ${style.bg} backdrop-blur-xl shadow-2xl animate-in slide-in-from-bottom-6 duration-300 ${
        style.pulse ? "animate-pulse" : ""
      }`}
      role="alert"
      aria-live={caption.urgency === "critical" ? "assertive" : "polite"}
    >
      <button onClick={onDismiss} className="w-full p-4 flex items-center gap-3 text-left">
        {style.icon}
        <p className={`text-sm font-semibold ${style.text} flex-1`}>{caption.display_text}</p>
        <span className="text-[10px] uppercase tracking-wider text-slate-400 bg-slate-800/60 px-2 py-0.5 rounded-full">
          {caption.urgency}
        </span>
      </button>
    </div>
  );
}
