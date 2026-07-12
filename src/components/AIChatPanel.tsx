import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Square, Sparkles, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
// ScrollArea removed - not used
import type { ChatMessage } from "@/hooks/useChat";

interface AIChatPanelProps {
  messages: ChatMessage[];
  streamingText: string;
  loading: boolean;
  onSend: (message: string) => void;
  onStop: () => void;
  onClear: () => void;
}

export function AIChatPanel({ messages, streamingText, loading, onSend, onStop, onClear }: AIChatPanelProps) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamingText]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="flex flex-col h-full glass-card rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg glass-subtle">
            <Bot className="h-4 w-4" style={{ color: "var(--theme-accent)" }} />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">AI Navigator</h3>
            <p className="text-[10px] text-slate-400 flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Powered by Multi-Agent System
            </p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClear}
          className="h-8 w-8 text-slate-500 hover:text-red-400 hover:bg-red-950/30"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
        {messages.length === 0 && !streamingText && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <div className="p-4 rounded-2xl glass-subtle mb-4">
              <Sparkles className="h-8 w-8" style={{ color: "var(--theme-accent)" }} />
            </div>
            <h4 className="text-sm font-medium text-slate-300 mb-1">Ask me anything about the stadium</h4>
            <p className="text-xs text-slate-500 max-w-[240px]">
              I can help with routes, accessibility info, crowd status, and more using my AI agents.
            </p>
            <div className="flex flex-wrap justify-center gap-2 mt-4">
              {["Find me a route", "Is it crowded?", "Where is the elevator?"].map((q) => (
                <button
                  key={q}
                  onClick={() => onSend(q)}
                  className="px-3 py-1.5 text-xs rounded-full glass-subtle text-slate-400 hover:text-white transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "assistant" && (
              <div className="shrink-0 w-7 h-7 rounded-lg glass-subtle flex items-center justify-center">
                <Bot className="h-4 w-4" style={{ color: "var(--theme-accent)" }} />
              </div>
            )}
            <div
              className={`max-w-[80%] px-3.5 py-2.5 rounded-xl text-sm leading-relaxed ${
                msg.role === "user"
                  ? "glass-subtle text-slate-200"
                  : "glass-subtle text-slate-300"
              }`}
              style={msg.role === "user" ? { borderColor: "var(--theme-border)", boxShadow: `0 0 10px var(--theme-glow)` } : undefined}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.agent_name && (
                <div className="text-[10px] text-slate-500 mt-1.5 flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  via {msg.agent_name}
                </div>
              )}
            </div>
            {msg.role === "user" && (
              <div className="shrink-0 w-7 h-7 rounded-lg glass-subtle flex items-center justify-center">
                <User className="h-4 w-4" style={{ color: "var(--theme-accent)" }} />
              </div>
            )}
          </div>
        ))}

        {streamingText && (
          <div className="flex gap-3">
            <div className="shrink-0 w-7 h-7 rounded-lg glass-subtle flex items-center justify-center">
              <Bot className="h-4 w-4 animate-pulse" style={{ color: "var(--theme-accent)" }} />
            </div>
            <div className="max-w-[80%] px-3.5 py-2.5 rounded-xl glass-subtle text-sm text-slate-300">
              <div className="whitespace-pre-wrap">{streamingText}</div>
              <div className="flex items-center gap-1 mt-1.5">
                <span className="h-1.5 w-1.5 rounded-full animate-pulse" style={{ background: "var(--theme-accent)" }} />
                <span className="text-[10px] text-slate-500">Streaming...</span>
              </div>
            </div>
          </div>
        )}

        {loading && !streamingText && (
          <div className="flex gap-3">
            <div className="shrink-0 w-7 h-7 rounded-lg glass-subtle flex items-center justify-center">
              <Bot className="h-4 w-4" style={{ color: "var(--theme-accent)" }} />
            </div>
            <div className="px-3.5 py-2.5 rounded-xl glass-subtle">
              <div className="flex items-center gap-2">
                <Loader2 className="h-3.5 w-3.5 animate-spin" style={{ color: "var(--theme-accent)" }} />
                <span className="text-xs text-slate-400">AI agents are thinking...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-white/5">
        <div className="flex gap-2">
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask the AI Navigator..."
            className="flex-1 glass-input text-slate-200 placeholder:text-slate-600 h-10"
            disabled={loading}
          />
          {loading ? (
            <Button
              type="button"
              onClick={onStop}
              variant="destructive"
              size="icon"
              className="h-10 w-10 bg-red-950/50 border border-red-800 hover:bg-red-900/50"
            >
              <Square className="h-4 w-4" />
            </Button>
          ) : (
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim()}
              className="h-10 w-10 btn-theme"
            >
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      </form>
    </div>
  );
}
