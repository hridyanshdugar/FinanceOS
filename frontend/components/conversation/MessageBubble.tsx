"use client";

import { Eye } from "lucide-react";
import { useAppStore } from "@/lib/store";
import type { ConversationMessage } from "@/lib/types";

interface MessageBubbleProps {
  message: ConversationMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const { setArtifactOpen, setCurrentAnalysis, setCurrentTaskId } = useAppStore();
  const isAdvisor = message.role === "advisor";

  return (
    <div className={`flex ${isAdvisor ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] ${
          isAdvisor
            ? "bg-foreground text-white rounded-2xl rounded-br-md px-4 py-3"
            : "bg-card border border-border rounded-2xl rounded-bl-md px-5 py-4"
        }`}
      >
        {!isAdvisor && (
          <p className="text-[11px] font-medium text-primary mb-1.5">Shadow</p>
        )}
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </div>

        {message.analysis && (
          <button
            onClick={() => {
              setCurrentAnalysis(message.analysis!);
              setCurrentTaskId(message.task_id || null);
              setArtifactOpen(true);
            }}
            className="mt-3 flex items-center gap-1.5 text-xs font-medium text-primary hover:text-primary/80 transition-colors"
          >
            <Eye className="h-3.5 w-3.5" />
            View full analysis
          </button>
        )}

        <p className={`text-[10px] mt-2 ${isAdvisor ? "text-white/50" : "text-muted-foreground"}`}>
          {new Date(message.timestamp).toLocaleTimeString("en-CA", {
            hour: "numeric",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}
