import { useState, useCallback, useRef } from "react";
import { API_ENDPOINTS } from "@/config/api";

export interface ChatMessage {
  role: "user" | "assistant" | "agent";
  content: string;
  agent_name?: string;
  timestamp?: string;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (
      message: string,
      stadiumId: string,
      accessibilityNeed: string,
      useStreaming: boolean = false
    ) => {
      const userMsg: ChatMessage = { role: "user", content: message };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setStreamingText("");

      try {
        if (useStreaming) {
          const controller = new AbortController();
          abortRef.current = controller;

          const res = await fetch(API_ENDPOINTS.chatStream, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              user_id: "user_001",
              stadium_id: stadiumId,
              accessibility_need: accessibilityNeed,
              message,
              use_streaming: true,
            }),
            signal: controller.signal,
          });

          const reader = res.body?.getReader();
          const decoder = new TextDecoder();
          let fullText = "";

          if (reader) {
            while (true) {
              const { done, value } = await reader.read();
              if (done) break;

              const chunk = decoder.decode(value);
              const lines = chunk.split("\n");
              for (const line of lines) {
                if (line.startsWith("data: ")) {
                  try {
                    const data = JSON.parse(line.slice(6));
                    if (data.token) {
                      fullText += data.token;
                      setStreamingText(fullText);
                    }
                    if (data.done) {
                      setMessages((prev) => [
                        ...prev,
                        { role: "assistant", content: fullText },
                      ]);
                      setStreamingText("");
                    }
                  } catch {
                    // skip invalid JSON
                  }
                }
              }
            }
          }
        } else {
          const res = await fetch(API_ENDPOINTS.chat, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              user_id: "user_001",
              stadium_id: stadiumId,
              accessibility_need: accessibilityNeed,
              message,
            }),
          });
          if (!res.ok) throw new Error("Chat request failed");
          const data = await res.json();
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: data.response, agent_name: data.agent_used },
          ]);
        }
      } catch (err) {
        if (err instanceof Error && err.name !== "AbortError") {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "Sorry, I'm having trouble connecting. Please try again.",
            },
          ]);
        }
      } finally {
        setLoading(false);
        abortRef.current = null;
      }
    },
    []
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    setLoading(false);
    if (streamingText) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: streamingText },
      ]);
      setStreamingText("");
    }
  }, [streamingText]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setStreamingText("");
  }, []);

  return { messages, loading, streamingText, sendMessage, stopStreaming, clearChat };
}
