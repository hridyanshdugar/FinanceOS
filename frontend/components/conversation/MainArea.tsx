"use client";

import { useEffect, useRef, useState } from "react";
import { useAppStore } from "@/lib/store";
import { MorningBriefing } from "./MorningBriefing";
import { ClientWorkspace } from "./ClientWorkspace";

export function MainArea() {
  const { selectedClientId } = useAppStore();
  const prevId = useRef(selectedClientId);
  const isFirstRender = useRef(true);
  const [showLoader, setShowLoader] = useState(false);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (prevId.current === selectedClientId) return;
    prevId.current = selectedClientId;
    setShowLoader(true);
    const timer = setTimeout(() => setShowLoader(false), 300);
    return () => clearTimeout(timer);
  }, [selectedClientId]);

  return (
    <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
      {showLoader ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="flex gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-loader-dot [animation-delay:0ms]" />
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-loader-dot [animation-delay:150ms]" />
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-loader-dot [animation-delay:300ms]" />
          </div>
        </div>
      ) : (
        <div
          key={selectedClientId ?? "home"}
          className="flex-1 flex flex-col min-w-0 h-full overflow-hidden animate-workspace-enter"
        >
          {selectedClientId ? <ClientWorkspace /> : <MorningBriefing />}
        </div>
      )}
    </div>
  );
}
