"use client";

import { BookOpen, Calculator, Shield, CheckCircle2, Loader2, Sparkles } from "lucide-react";
import { useAppStore } from "@/lib/store";

const AGENT_META: Record<string, { icon: React.ReactNode; label: string }> = {
  context: { icon: <BookOpen className="h-3.5 w-3.5" />, label: "Context Agent" },
  quant: { icon: <Calculator className="h-3.5 w-3.5" />, label: "Quant Agent" },
  compliance: { icon: <Shield className="h-3.5 w-3.5" />, label: "Compliance Agent" },
};

export function ThinkingIndicator() {
  const { thinkingStep, thinkingAgents } = useAppStore();
  const agents = Object.entries(thinkingAgents);

  return (
    <div className="flex justify-start">
      <div className="bg-card border border-border rounded-2xl rounded-bl-md px-5 py-4 max-w-md w-full">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          <p className="text-[11px] font-semibold text-primary">Shadow is thinking</p>
        </div>

        {thinkingStep && (
          <p className="text-xs text-muted-foreground mb-3 italic">{thinkingStep}</p>
        )}

        {agents.length > 0 && (
          <div className="space-y-2">
            {agents.map(([agentName, agentState]) => {
              const meta = AGENT_META[agentName] || { icon: null, label: agentName };
              const isComplete = agentState.status === "completed";

              return (
                <div key={agentName} className="flex items-start gap-2.5">
                  <div className={`mt-0.5 ${isComplete ? "text-green-600" : "text-primary"}`}>
                    {isComplete ? (
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    ) : (
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-xs font-medium ${isComplete ? "text-muted-foreground" : "text-foreground"}`}>
                      {meta.label}
                    </p>
                    {agentState.description && (
                      <p className="text-[11px] text-muted-foreground mt-0.5 leading-relaxed">
                        {agentState.description}
                      </p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {agents.length === 0 && (
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot" />
            <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot-delay-1" />
            <span className="h-2 w-2 rounded-full bg-muted-foreground animate-pulse-dot-delay-2" />
          </div>
        )}
      </div>
    </div>
  );
}
