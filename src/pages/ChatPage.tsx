import { AIChatPanel } from "@/components/AIChatPanel";
import { GlassCard } from "@/components/GlassCard";
import { useChat } from "@/hooks/useChat";
import { MessageSquare, Sparkles, Shield, Zap, Brain } from "lucide-react";

interface ChatPageProps {
  stadiumId: string;
}

export function ChatPage({ stadiumId }: ChatPageProps) {
  const { messages, loading, streamingText, sendMessage, stopStreaming, clearChat } = useChat();

  const handleSend = (message: string) => {
    sendMessage(message, stadiumId, "wheelchair", false);
  };

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col">
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 p-4 min-h-0">
        {/* Info Panel */}
        <div className="hidden lg:flex flex-col gap-4">
          <GlassCard tilt maxTilt={3} className="rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <span
                className="p-1.5 rounded-lg"
                style={{
                  background: "var(--theme-bg)",
                  color: "var(--theme-accent)",
                  boxShadow: "0 0 12px var(--theme-glow)",
                }}
              >
                <MessageSquare className="h-5 w-5" />
              </span>
              <h3 className="text-sm font-semibold text-white">AI Assistant</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Ask me anything about navigating the stadium. I use multiple AI agents to help you find the best routes and information.
            </p>
            <div className="space-y-2">
              {[
                { icon: <Brain className="h-3.5 w-3.5" />, label: "Natural language understanding", color: "#a78bfa" },
                { icon: <Zap className="h-3.5 w-3.5" />, label: "Real-time route planning", color: "#fbbf24" },
                { icon: <Shield className="h-3.5 w-3.5" />, label: "Accessibility-aware responses", color: "#34d399" },
                { icon: <Sparkles className="h-3.5 w-3.5" />, label: "Multi-agent AI system", color: "#22d3ee" },
              ].map((feature) => (
                <div key={feature.label} className="flex items-center gap-2 text-xs text-slate-300">
                  <span
                    className="p-1 rounded-md shrink-0"
                    style={{
                      background: `${feature.color}22`,
                      color: feature.color,
                      boxShadow: `0 0 6px ${feature.color}66`,
                    }}
                  >
                    {feature.icon}
                  </span>
                  {feature.label}
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard tilt maxTilt={3} className="rounded-xl p-4 flex-1">
            <h4 className="text-xs font-semibold text-slate-300 mb-3">Example Questions</h4>
            <div className="space-y-2">
              {[
                "Find me a route to upper deck",
                "Is the north ramp crowded?",
                "Where is the nearest elevator?",
                "Best path for wheelchair users?",
                "What's the crowd situation?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  className="w-full text-left px-3 py-2 rounded-lg glass-3d-subtle text-xs text-slate-300 hover:text-white hover:border-white/20 transition-all hover:-translate-y-0.5"
                >
                  {q}
                </button>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Chat */}
        <div className="lg:col-span-3 h-full min-h-0">
          <AIChatPanel
            messages={messages}
            streamingText={streamingText}
            loading={loading}
            onSend={handleSend}
            onStop={stopStreaming}
            onClear={clearChat}
          />
        </div>
      </div>
    </div>
  );
}
