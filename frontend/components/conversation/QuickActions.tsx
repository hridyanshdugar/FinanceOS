"use client";

import { useAppStore } from "@/lib/store";
import { useWsSend } from "@/components/layout/AppShell";

const SUGGESTIONS = [
  "Check contribution room",
  "Run a portfolio review",
  "Draft a check-in email",
  "Compare TFSA vs RRSP",
];

interface QuickActionsProps {
  clientName: string;
}

export function QuickActions({ clientName }: QuickActionsProps) {
  const { addMessage, selectedClientId, setIsThinking } = useAppStore();
  const sendWs = useWsSend();

  const handleClick = (suggestion: string) => {
    if (!selectedClientId) return;
    const content = `${suggestion} for ${clientName}`;

    addMessage({
      id: crypto.randomUUID(),
      role: "advisor",
      content,
      timestamp: new Date().toISOString(),
    });

    setIsThinking(true);
    sendWs({
      type: "chat_message",
      client_id: selectedClientId,
      content,
    });
  };

  return (
    <div className="mt-8">
      <p className="text-xs text-muted-foreground mb-3">Quick actions</p>
      <div className="flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => handleClick(s)}
            className="px-3.5 py-2 text-sm rounded-xl bg-card border border-border
                     text-muted-foreground hover:text-foreground hover:border-primary/30
                     hover:shadow-sm transition-all duration-150"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
