"use client";

import { BookOpen, Calculator, Shield, TrendingUp, CheckCircle2, Loader2, Brain } from "lucide-react";
import { useAppStore } from "@/lib/store";

const AGENT_META: Record<string, { icon: React.ReactNode; label: string; color: string }> = {
  context: { icon: <BookOpen className="h-3.5 w-3.5" />, label: "Context", color: "text-blue-600" },
  quant: { icon: <Calculator className="h-3.5 w-3.5" />, label: "Quant", color: "text-amber-600" },
  compliance: { icon: <Shield className="h-3.5 w-3.5" />, label: "Compliance", color: "text-emerald-600" },
  researcher: { icon: <TrendingUp className="h-3.5 w-3.5" />, label: "Research", color: "text-violet-600" },
};

export function ThinkingIndicator() {
  const { thinkingStep, thinkingAgents } = useAppStore();
  const agents = Object.entries(thinkingAgents);
  const completedCount = agents.filter(([, s]) => s.status === "completed").length;
  const totalCount = agents.length;

  return (
    <div className="flex justify-start">
      <div className="bg-card border border-border rounded-2xl rounded-bl-md px-5 py-4 max-w-md w-full">
        {/* Header */}
        <div className="flex items-center gap-2.5">
          <div className="relative h-7 w-7 rounded-lg bg-primary/10 flex items-center justify-center">
            <Brain className="h-4 w-4 text-primary" />
            <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-primary animate-pulse" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-semibold text-foreground">Shadow</p>
            {thinkingStep && (
              <p className="text-[11px] text-muted-foreground leading-snug">{thinkingStep}</p>
            )}
          </div>
        </div>

        {/* Agent progress */}
        {totalCount > 0 && (
          <div className="mt-3 space-y-1.5">
            {/* Progress bar */}
            <div className="h-1 rounded-full bg-accent overflow-hidden">
              <div
                className="h-full rounded-full bg-primary transition-all duration-500 ease-out"
                style={{ width: `${totalCount > 0 ? (completedCount / totalCount) * 100 : 0}%` }}
              />
            </div>

            {/* Agent chips */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {agents.map(([agentName, agentState]) => {
                const meta = AGENT_META[agentName] || { icon: null, label: agentName, color: "text-primary" };
                const isComplete = agentState.status === "completed";

                return (
                  <div
                    key={agentName}
                    className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-medium transition-all duration-300 ${
                      isComplete
                        ? "bg-green-50 text-green-700 border border-green-100"
                        : "bg-accent/70 text-foreground border border-border"
                    }`}
                  >
                    {isComplete ? (
                      <CheckCircle2 className="h-3 w-3 text-green-600" />
                    ) : (
                      <Loader2 className="h-3 w-3 animate-spin text-primary" />
                    )}
                    <span className={meta.color}>{meta.icon}</span>
                    {meta.label}
                  </div>
                );
              })}
            </div>

            {/* Agent descriptions */}
            {agents.some(([, s]) => s.status !== "completed" && s.description) && (
              <div className="pt-1">
                {agents
                  .filter(([, s]) => s.status !== "completed" && s.description)
                  .map(([agentName, agentState]) => (
                    <p key={agentName} className="text-[10px] text-muted-foreground italic leading-relaxed">
                      {agentState.description}
                    </p>
                  ))}
              </div>
            )}
          </div>
        )}

        {/* No agents — direct processing */}
        {totalCount === 0 && (
          <div className="mt-2.5 flex items-center gap-2">
            <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
            <p className="text-[11px] text-muted-foreground">Processing...</p>
          </div>
        )}
      </div>
    </div>
  );
}
