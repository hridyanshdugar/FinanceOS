"use client";

import { useEffect, useRef } from "react";
import { Brain } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { MessageBubble } from "./MessageBubble";
import { ThinkingIndicator } from "./ThinkingIndicator";

export function ConversationThread() {
  const {
    clientDetail,
    conversation,
    isThinking,
  } = useAppStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation, isThinking]);

  if (!clientDetail) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-16 rounded-2xl animate-shimmer" />
        ))}
      </div>
    );
  }

  const { client } = clientDetail;

  return (
    <div className="animate-fade-in-up">
      {conversation.length === 0 && !isThinking && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="h-12 w-12 rounded-2xl bg-accent flex items-center justify-center mb-4">
            <Brain className="h-6 w-6 text-primary" />
          </div>
          <h3 className="text-lg font-semibold text-foreground">
            How can I help with {client.name.split(" ")[0]}?
          </h3>
          <p className="text-sm text-muted-foreground mt-1.5 max-w-sm">
            Ask a question, run an analysis, or pick a quick action below.
          </p>
        </div>
      )}
      <div className="space-y-6">
        {conversation.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isThinking && <ThinkingIndicator />}
      </div>
      <div ref={bottomRef} />
    </div>
  );
}
