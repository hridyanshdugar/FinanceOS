"use client";

import { useState } from "react";
import { ShieldCheck, ShieldAlert, ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface ComplianceSectionProps {
  data: {
    status: "clear" | "warning" | "error";
    items: Array<{
      severity: "info" | "warning" | "error";
      message: string;
      rule_citation?: string;
    }>;
  };
}

export function ComplianceSection({ data }: ComplianceSectionProps) {
  const [expanded, setExpanded] = useState(false);
  const isClear = data.status === "clear";

  return (
    <div className="rounded-2xl border border-border bg-background p-4">
      <div className="flex items-center gap-2 mb-3">
        <div
          className={cn(
            "h-7 w-7 rounded-lg flex items-center justify-center",
            isClear ? "bg-emerald-50 text-emerald-600" : "bg-amber-50 text-amber-600"
          )}
        >
          {isClear ? (
            <ShieldCheck className="h-3.5 w-3.5" />
          ) : (
            <ShieldAlert className="h-3.5 w-3.5" />
          )}
        </div>
        <h4 className="text-sm font-semibold text-foreground">Compliance Check</h4>
        {isClear && (
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 font-medium">
            All clear
          </span>
        )}
      </div>

      {data.items.length > 0 && (
        <div className="space-y-2">
          {data.items.slice(0, expanded ? undefined : 2).map((item, i) => (
            <div
              key={i}
              className={cn(
                "text-sm px-3 py-2 rounded-xl",
                item.severity === "error"
                  ? "bg-red-50 text-red-700"
                  : item.severity === "warning"
                  ? "bg-amber-50 text-amber-700"
                  : "bg-blue-50 text-blue-700"
              )}
            >
              {item.message}
              {item.rule_citation && (
                <span className="block text-[10px] mt-0.5 opacity-70">
                  {item.rule_citation}
                </span>
              )}
            </div>
          ))}

          {data.items.length > 2 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              {expanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
              {expanded ? "Show less" : `${data.items.length - 2} more`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
