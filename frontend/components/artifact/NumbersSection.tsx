"use client";

import { useState } from "react";
import { Calculator, ChevronDown, ChevronRight, Code } from "lucide-react";

interface NumbersSectionProps {
  data: {
    summary: string;
    details: string;
    python_code?: string;
    latex?: string;
  };
}

export function NumbersSection({ data }: NumbersSectionProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [showCode, setShowCode] = useState(false);

  return (
    <div className="rounded-2xl border border-border bg-background p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-7 w-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
          <Calculator className="h-3.5 w-3.5" />
        </div>
        <h4 className="text-sm font-semibold text-foreground">The Numbers</h4>
      </div>

      <p className="text-sm text-foreground leading-relaxed">{data.summary}</p>

      {data.details && (
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="mt-3 flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
        >
          {showDetails ? (
            <ChevronDown className="h-3.5 w-3.5" />
          ) : (
            <ChevronRight className="h-3.5 w-3.5" />
          )}
          See how we got here
        </button>
      )}

      {showDetails && (
        <div className="mt-3 p-3 rounded-xl bg-muted text-xs text-muted-foreground leading-relaxed whitespace-pre-wrap">
          {data.details}

          {data.python_code && (
            <>
              <button
                onClick={() => setShowCode(!showCode)}
                className="mt-3 flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                <Code className="h-3 w-3" />
                {showCode ? "Hide code" : "View code"}
              </button>

              {showCode && (
                <pre className="mt-2 p-3 rounded-lg bg-foreground/5 text-[11px] font-mono overflow-x-auto">
                  {data.python_code}
                </pre>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
