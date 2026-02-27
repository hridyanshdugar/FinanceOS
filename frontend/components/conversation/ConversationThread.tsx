"use client";

import { useEffect, useRef } from "react";
import { useAppStore } from "@/lib/store";
import { api } from "@/lib/api";
import { MessageBubble } from "./MessageBubble";
import { ThinkingIndicator } from "./ThinkingIndicator";
import { QuickActions } from "./QuickActions";
import type { ClientDetail, ConversationMessage } from "@/lib/types";

export function ConversationThread() {
  const {
    selectedClientId,
    clientDetail,
    setClientDetail,
    conversation,
    setConversation,
    isThinking,
  } = useAppStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!selectedClientId) return;
    api.getClient(selectedClientId).then((data) => {
      const detail = data as unknown as ClientDetail;
      setClientDetail(detail);
      const existingMessages: ConversationMessage[] = detail.chat_history.map((ch) => ({
        id: ch.id,
        role: ch.role === "advisor" ? "advisor" : "shadow",
        content: ch.content,
        timestamp: ch.created_at,
      }));
      setConversation(existingMessages);
    });
  }, [selectedClientId, setClientDetail, setConversation]);

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
      {/* Client Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <h2 className="text-2xl font-semibold text-foreground tracking-tight">
            {client.name}
          </h2>
          <span className="text-xs px-2.5 py-1 rounded-full bg-accent text-muted-foreground font-medium">
            {client.risk_profile}
          </span>
          <span className="text-xs text-muted-foreground">
            {client.province}
          </span>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Portfolio: ${clientDetail.total_portfolio.toLocaleString("en-CA")} ·{" "}
          {client.employer || "Self-employed"}
        </p>
      </div>

      {/* Messages */}
      <div className="space-y-6">
        {conversation.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isThinking && <ThinkingIndicator />}
      </div>

      {/* Quick Actions (when no active conversation) */}
      {conversation.length === 0 && !isThinking && (
        <QuickActions clientName={client.name} />
      )}

      <div ref={bottomRef} />
    </div>
  );
}
