import { useState } from "react";
import { FlaskConical, RotateCcw, AlertTriangle, Clock, DoorOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/GlassCard";
import { API_ENDPOINTS } from "@/config/api";
import { toast } from "sonner";

interface DemoControlsProps {
  stadiumId: string;
  onScenarioTriggered: () => void;
}

type ScenarioType = "normal" | "blocked" | "emergency" | "halftime" | "evacuation";

const scenarios: { type: ScenarioType; label: string; icon: React.ReactNode; color: string }[] = [
  { type: "normal", label: "Normal", icon: <RotateCcw className="h-4 w-4" />, color: "#34d399" },
  { type: "blocked", label: "Blocked", icon: <AlertTriangle className="h-4 w-4" />, color: "#fbbf24" },
  { type: "halftime", label: "Halftime", icon: <Clock className="h-4 w-4" />, color: "#22d3ee" },
  { type: "evacuation", label: "Evacuation", icon: <DoorOpen className="h-4 w-4" />, color: "#fb923c" },
];

export function DemoControls({ stadiumId, onScenarioTriggered }: DemoControlsProps) {
  const [loading, setLoading] = useState<ScenarioType | null>(null);

  const triggerScenario = async (type: ScenarioType) => {
    setLoading(type);
    try {
      const res = await fetch(API_ENDPOINTS.demoScenario, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario_type: type, stadium_id: stadiumId }),
      });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      toast.success(`${data.description} (${data.zones_affected} zones)`);
      onScenarioTriggered();
    } catch {
      toast.error("Failed to trigger scenario");
    } finally {
      setLoading(null);
    }
  };

  return (
    <GlassCard tilt maxTilt={3} className="rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <span
          className="p-1.5 rounded-lg"
          style={{ background: "#a78bfa22", color: "#a78bfa", boxShadow: "0 0 10px #a78bfa66" }}
        >
          <FlaskConical className="h-4 w-4" />
        </span>
        <h3 className="text-sm font-semibold text-white">Demo Scenarios</h3>
      </div>
      <div className="flex flex-wrap gap-2">
        {scenarios.map((s) => (
          <Button
            key={s.type}
            variant="outline"
            size="sm"
            onClick={() => triggerScenario(s.type)}
            disabled={loading !== null}
            className="glass-3d-subtle text-xs h-8 hover:bg-white/10 transition-transform active:scale-95 hover:-translate-y-0.5"
            style={{ color: s.color }}
          >
            {loading === s.type ? (
              <RotateCcw className="h-3.5 w-3.5 animate-spin mr-1.5" />
            ) : (
              <>
                {s.icon}
                <span className="ml-1.5">{s.label}</span>
              </>
            )}
          </Button>
        ))}
      </div>
    </GlassCard>
  );
}
