"use client";

import { useEffect, useRef } from "react";
import { useAppStore } from "@/lib/store";
import { MessageBubble } from "./MessageBubble";
import { ThinkingIndicator } from "./ThinkingIndicator";
import { QuickActions } from "./QuickActions";

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
      {/* Messages */}
      <div className="space-y-6">
        {conversation.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isThinking && <ThinkingIndicator />}
      </div>

      {conversation.length === 0 && !isThinking && (
        <QuickActions clientName={client.name} />
      )}

      <div ref={bottomRef} />
    </div>
  );
}
