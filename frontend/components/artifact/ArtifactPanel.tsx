"use client";

import { X, Sparkles } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { NumbersSection } from "./NumbersSection";
import { ResearchSection } from "./ResearchSection";
import { ComplianceSection } from "./ComplianceSection";
import { DraftMessage } from "./DraftMessage";
import { ActionBar } from "./ActionBar";

export function ArtifactPanel() {
  const { setArtifactOpen, currentAnalysis } = useAppStore();

  return (
    <div className="w-[420px] h-full border-l border-border bg-card flex flex-col shrink-0 animate-slide-in">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <h3 className="text-sm font-semibold text-foreground">Analysis</h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">
            Ready for your review
          </span>
        </div>
        <button
          onClick={() => setArtifactOpen(false)}
          className="h-7 w-7 rounded-lg flex items-center justify-center hover:bg-accent transition-colors"
        >
          <X className="h-4 w-4 text-muted-foreground" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-5 py-5 space-y-6">
        {currentAnalysis ? (
          <>
            <NumbersSection data={currentAnalysis.numbers} />
            {currentAnalysis.research && (
              <ResearchSection data={currentAnalysis.research} />
            )}
            <ComplianceSection data={currentAnalysis.compliance} />
            <DraftMessage data={currentAnalysis.draft_message} />
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-sm text-muted-foreground">
              No analysis to display yet.
            </p>
          </div>
        )}
      </div>

      {/* Action Bar */}
      {currentAnalysis && <ActionBar />}
    </div>
  );
}
