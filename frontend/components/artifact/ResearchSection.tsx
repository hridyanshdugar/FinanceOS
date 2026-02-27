"use client";

import { useState } from "react";
import { TrendingUp, ChevronDown, ChevronRight } from "lucide-react";
import type { ResearchOutput } from "@/lib/types";

interface ResearchSectionProps {
  data: ResearchOutput;
}

function AssetMixBar({ equity, fixedIncome, alternatives }: { equity: number; fixedIncome: number; alternatives: number }) {
  const total = equity + fixedIncome + alternatives;
  if (total === 0) return null;

  return (
    <div className="space-y-1.5">
      <div className="flex h-2.5 rounded-full overflow-hidden">
        {equity > 0 && (
          <div className="bg-violet-500 transition-all" style={{ width: `${equity}%` }} />
        )}
        {fixedIncome > 0 && (
          <div className="bg-blue-400 transition-all" style={{ width: `${fixedIncome}%` }} />
        )}
        {alternatives > 0 && (
          <div className="bg-amber-400 transition-all" style={{ width: `${alternatives}%` }} />
        )}
      </div>
      <div className="flex gap-3 text-[10px] text-muted-foreground">
        {equity > 0 && (
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-violet-500" />Equity {equity}%
          </span>
        )}
        {fixedIncome > 0 && (
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-blue-400" />Fixed Income {fixedIncome}%
          </span>
        )}
        {alternatives > 0 && (
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-amber-400" />Alternatives {alternatives}%
          </span>
        )}
      </div>
    </div>
  );
}

export function ResearchSection({ data }: ResearchSectionProps) {
  const [showStrategy, setShowStrategy] = useState(false);

  return (
    <div className="rounded-2xl border border-border bg-background p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-7 w-7 rounded-lg bg-violet-50 text-violet-600 flex items-center justify-center">
          <TrendingUp className="h-3.5 w-3.5" />
        </div>
        <h4 className="text-sm font-semibold text-foreground">Investment Research</h4>
      </div>

      <p className="text-sm text-foreground leading-relaxed mb-4">{data.summary}</p>

      {data.asset_mix && (
        <div className="mb-4">
          <AssetMixBar
            equity={data.asset_mix.equity_pct}
            fixedIncome={data.asset_mix.fixed_income_pct}
            alternatives={data.asset_mix.alternatives_pct}
          />
        </div>
      )}

      {data.suggestions.length > 0 && (
        <div className="space-y-2">
          {data.suggestions.map((s, i) => (
            <div key={i} className="flex items-start gap-3 p-2.5 rounded-xl bg-muted/50">
              <div className="shrink-0 h-8 min-w-[3.5rem] rounded-lg bg-violet-50 text-violet-700 flex items-center justify-center text-[11px] font-bold tracking-wide">
                {s.ticker}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-xs font-medium text-foreground truncate">{s.name}</p>
                  {s.allocation_pct > 0 && (
                    <span className="shrink-0 text-[10px] px-1.5 py-0.5 rounded-full bg-violet-50 text-violet-700 font-medium">
                      {s.allocation_pct}%
                    </span>
                  )}
                </div>
                <p className="text-[11px] text-muted-foreground leading-relaxed mt-0.5">{s.rationale}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {data.account_strategy && (
        <>
          <button
            onClick={() => setShowStrategy(!showStrategy)}
            className="mt-3 flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            {showStrategy ? (
              <ChevronDown className="h-3.5 w-3.5" />
            ) : (
              <ChevronRight className="h-3.5 w-3.5" />
            )}
            Account placement strategy
          </button>
          {showStrategy && (
            <div className="mt-2 p-3 rounded-xl bg-muted text-xs text-muted-foreground leading-relaxed">
              {data.account_strategy}
            </div>
          )}
        </>
      )}
    </div>
  );
}
