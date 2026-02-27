"use client";

import { useState, useRef, useEffect } from "react";
import { SendHorizontal } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { useWsSend } from "@/components/layout/AppShell";

const ACTION_SUGGESTIONS = [
  "Check contribution room",
  "Suggest investments",
  "Run a portfolio review",
  "Draft a check-in email",
  "Compare TFSA vs RRSP",
  "Check compliance",
];

export function useSendMessage() {
  const { selectedClientId, addMessage, isThinking, setIsThinking } = useAppStore();
  const sendWs = useWsSend();

  return (content: string) => {
    if (!content || !selectedClientId || isThinking) return;
    addMessage({
      id: crypto.randomUUID(),
      role: "advisor",
      content,
      timestamp: new Date().toISOString(),
    });
    setIsThinking(true);
    sendWs({ type: "chat_message", client_id: selectedClientId, content });
  };
}

export { ACTION_SUGGESTIONS };

export function InputBar() {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const { selectedClientId, isThinking } = useAppStore();
  const sendMessage = useSendMessage();

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 150) + "px";
    }
  }, [input]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    sendMessage(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-border bg-card px-6 py-4">
      <div className="max-w-3xl mx-auto">
        <div className="relative flex items-end gap-2 rounded-2xl border border-border bg-background px-4 py-3
                      focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              selectedClientId
                ? "What should we look into?"
                : "Select a client to get started..."
            }
            disabled={!selectedClientId || isThinking}
            rows={1}
            className="flex-1 resize-none bg-transparent text-sm text-foreground
                     placeholder:text-muted-foreground focus:outline-none disabled:opacity-50
                     min-h-[24px] max-h-[150px]"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || !selectedClientId || isThinking}
            className="shrink-0 h-8 w-8 rounded-xl bg-primary text-primary-foreground
                     flex items-center justify-center hover:bg-primary/90 transition-colors
                     disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <SendHorizontal className="h-4 w-4" />
          </button>
        </div>
        <p className="text-[10px] text-muted-foreground text-center mt-2">
          Shadow assists your decisions. All actions require your approval.
        </p>
      </div>
    </div>
  );
}
