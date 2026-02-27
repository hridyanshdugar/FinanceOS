"use client";

import { useAppStore } from "@/lib/store";
import { MorningBriefing } from "./MorningBriefing";
import { ClientWorkspace } from "./ClientWorkspace";

export function MainArea() {
  const { selectedClientId } = useAppStore();

  return (
    <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
      {selectedClientId ? <ClientWorkspace /> : <MorningBriefing />}
    </div>
  );
}
