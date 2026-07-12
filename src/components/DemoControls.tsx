import { useState } from "react";
import { FlaskConical, RotateCcw, AlertTriangle, Clock, DoorOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { API_ENDPOINTS } from "@/config/api";
import { toast } from "sonner";

interface DemoControlsProps {
  stadiumId: string;
  onScenarioTriggered: () => void;
}

type ScenarioType = "normal" | "blocked" | "emergency" | "halftime" | "evacuation";

const scenarios: { type: ScenarioType; label: string; icon: React.ReactNode; color: string }[] = [
  { type: "normal", label: "Normal", icon: <RotateCcw className="h-4 w-4" />, color: "text-emerald-400" },
  { type: "blocked", label: "Blocked", icon: <AlertTriangle className="h-4 w-4" />, color: "text-amber-400" },
  { type: "halftime", label: "Halftime", icon: <Clock className="h-4 w-4" />, color: "text-cyan-400" },
  { type: "evacuation", label: "Evacuation", icon: <DoorOpen className="h-4 w-4" />, color: "text-orange-400" },
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
    <div className="glass-card rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <FlaskConical className="h-4 w-4 text-violet-400" />
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
            className={`glass-subtle ${s.color} text-xs h-8 hover:bg-white/10`}
          >
            {loading === s.type ? (
              <RotateCcw className="h-3.5 w-3.5 animate-spin mr-1.5" />
            ) : (
              <>{s.icon}<span className="ml-1.5">{s.label}</span></>
            )}
          </Button>
        ))}
      </div>
    </div>
  );
}
