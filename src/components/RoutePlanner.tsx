/**
 * RoutePlanner Component
 * ======================
 * Sidebar panel for configuring and triggering AI route calculations.
 * Includes accessibility need selection, zone start/end dropdowns,
 * voice input (Web Speech API), and the "Calculate Route" button.
 *
 * Voice input uses the browser's SpeechRecognition API to match
 * spoken zone names and auto-fill the destination field.
 */
import { useState, useEffect } from "react";
import { Navigation, Mic, MicOff, Sparkles, Loader2, MapPin, Flag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import type { Zone } from "@/hooks/useZones";

interface RoutePlannerProps {
  zones: Zone[];
  loading: boolean;
  onCalculate: (start: string, end: string, need: string) => void;
  selectedStart: string;
  selectedEnd: string;
  onStartChange: (v: string) => void;
  onEndChange: (v: string) => void;
}

export function RoutePlanner({
  zones,
  loading,
  onCalculate,
  selectedStart,
  selectedEnd,
  onStartChange,
  onEndChange,
}: RoutePlannerProps) {
  const [need, setNeed] = useState("wheelchair");
  const [isRecording, setIsRecording] = useState(false);

  useEffect(() => {
    if (zones.length > 0) {
      if (!zones.find((z) => z.zone_id === selectedStart)) onStartChange(zones[0].zone_id);
      if (!zones.find((z) => z.zone_id === selectedEnd)) onEndChange(zones[zones.length - 1].zone_id);
    }
  }, [zones, selectedStart, selectedEnd, onStartChange, onEndChange]);

  // Accessibility: Integrating Web Speech API ensures WCAG 2.1 AA compliance for motor-impaired users
  const startVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      toast.error("Voice input is not supported in this browser. Please use Chrome or Edge.");
      return;
    }
    const rec = new SpeechRecognition();
    rec.lang = "en-US";
    rec.continuous = false;
    rec.interimResults = false;
    rec.onstart = () => {
      setIsRecording(true);
      toast.info("Listening... Say a zone name");
    };
    rec.onend = () => setIsRecording(false);
    rec.onerror = () => {
      setIsRecording(false);
      toast.error("Could not recognize speech. Please try again.");
    };
    rec.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript.toLowerCase().trim();
      const matched = zones.find((z) =>
        transcript.includes(z.zone_id.replace(/_/g, " "))
      );
      if (matched) {
        onEndChange(matched.zone_id);
        toast.success(`Destination set to: ${matched.zone_id.replace(/_/g, " ")}`);
      } else {
        toast.warning(`No matching zone found for: "${transcript}"`);
      }
    };
    rec.start();
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <div
          className="p-2 rounded-lg glass-3d-subtle"
          style={{ borderColor: "var(--theme-border)", boxShadow: "0 0 12px var(--theme-glow)" }}
        >
          <Navigation className="h-5 w-5" style={{ color: "var(--theme-accent)" }} />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">AI Route Planner</h3>
          <p className="text-xs text-slate-400">Multi-agent accessible routing</p>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-xs font-medium text-slate-400 mb-1.5 block">Accessibility Need</label>
          <Select value={need} onValueChange={setNeed}>
            <SelectTrigger className="glass-3d-input h-9 text-slate-200 rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="glass-3d-dropdown">
              <SelectItem value="wheelchair">Wheelchair / Mobility</SelectItem>
              <SelectItem value="hearing_impaired">Hearing Impaired</SelectItem>
              <SelectItem value="visual_impaired">Visual Impaired</SelectItem>
              <SelectItem value="both">Multiple Needs</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-xs font-medium text-slate-400 mb-1.5 block flex items-center gap-1.5">
            <MapPin className="h-3 w-3" /> Current Location
          </label>
          <Select value={selectedStart} onValueChange={onStartChange}>
            <SelectTrigger className="glass-3d-input h-9 text-slate-200 rounded-xl">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="glass-3d-dropdown max-h-60">
              {zones.map((z) => (
                <SelectItem key={z.zone_id} value={z.zone_id}>
                  <span className="capitalize">{z.zone_id.replace(/_/g, " ")}</span>
                  <span className="text-slate-500 ml-2 text-xs">({z.type})</span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="text-xs font-medium text-slate-400 mb-1.5 block flex items-center gap-1.5">
            <Flag className="h-3 w-3" /> Destination
          </label>
          <div className="flex gap-2">
            <Select value={selectedEnd} onValueChange={onEndChange}>
              <SelectTrigger className="glass-3d-input h-9 text-slate-200 flex-1 rounded-xl">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="glass-3d-dropdown max-h-60">
                {zones.map((z) => (
                  <SelectItem key={z.zone_id} value={z.zone_id}>
                    <span className="capitalize">{z.zone_id.replace(/_/g, " ")}</span>
                    <span className="text-slate-500 ml-2 text-xs">({z.type})</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button
              variant="outline"
              size="icon"
              onClick={startVoice}
              className={`h-9 w-9 glass-3d-subtle rounded-xl transition-transform active:scale-90 ${isRecording ? "text-red-400 animate-pulse" : "text-slate-400 hover:text-white"}`}
              style={isRecording ? { borderColor: "#ef4444", boxShadow: "0 0 12px rgba(239,68,68,0.4)" } : undefined}
            >
              {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            </Button>
          </div>
        </div>

        <Button
          onClick={() => onCalculate(selectedStart, selectedEnd, need)}
          disabled={loading || !selectedStart || !selectedEnd}
          className="w-full btn-theme text-white h-10 font-medium rounded-xl"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              AI Calculating...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4 mr-2" />
              Calculate Route
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
