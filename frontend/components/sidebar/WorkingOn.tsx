"use client";

import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { useAppStore } from "@/lib/store";

const AGENT_LABELS: Record<string, string> = {
  context: "Reviewing history",
  quant: "Running calculations",
  researcher: "Researching markets",
  compliance: "Checking compliance",
};

export function WorkingOn() {
  const { agentTasks, selectedClientId } = useAppStore();
  const clientTasks = agentTasks.filter((t) => t.client_id === selectedClientId);
  const activeTasks = clientTasks.filter(
    (t) => t.status === "running" || t.status === "pending"
  );
  const recentDone = clientTasks
    .filter((t) => t.status === "completed" || t.status === "failed")
    .slice(0, 2);

  const visible = [...activeTasks, ...recentDone].slice(0, 4);

  if (visible.length === 0) return null;

  return (
    <div className="border-t border-border px-3 py-3">
      <p className="px-1 pb-2 text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
        Working on
      </p>
      <div className="space-y-1.5">
        {visible.map((task) => (
          <div
            key={task.id}
            className="flex items-center gap-2.5 px-2 py-1.5 rounded-lg text-xs"
          >
            {task.status === "running" || task.status === "pending" ? (
              <Loader2 className="h-3.5 w-3.5 text-primary animate-spin shrink-0" />
            ) : task.status === "completed" ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="h-3.5 w-3.5 text-destructive shrink-0" />
            )}
            <span className="text-muted-foreground truncate">
              {AGENT_LABELS[task.agent_type] || task.agent_type}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
