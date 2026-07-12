import { AIChatPanel } from "@/components/AIChatPanel";
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
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="h-5 w-5" style={{ color: "var(--theme-accent)" }} />
              <h3 className="text-sm font-semibold text-white">AI Assistant</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Ask me anything about navigating the stadium. I use multiple AI agents to help you find the best routes and information.
            </p>
            <div className="space-y-2">
              {[
                { icon: <Brain className="h-3.5 w-3.5" />, label: "Natural language understanding" },
                { icon: <Zap className="h-3.5 w-3.5" />, label: "Real-time route planning" },
                { icon: <Shield className="h-3.5 w-3.5" />, label: "Accessibility-aware responses" },
                { icon: <Sparkles className="h-3.5 w-3.5" />, label: "Multi-agent AI system" },
              ].map((feature) => (
                <div key={feature.label} className="flex items-center gap-2 text-xs text-slate-400">
                  <span style={{ color: "var(--theme-accent)" }}>{feature.icon}</span>
                  {feature.label}
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card rounded-xl p-4 flex-1">
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
                  className="w-full text-left px-3 py-2 rounded-lg glass-subtle text-xs text-slate-400 hover:text-white hover:border-white/20 transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
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
