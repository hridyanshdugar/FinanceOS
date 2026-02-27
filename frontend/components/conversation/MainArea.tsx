"use client";

import { useAppStore } from "@/lib/store";
import { MorningBriefing } from "./MorningBriefing";
import { ConversationThread } from "./ConversationThread";
import { InputBar } from "./InputBar";

export function MainArea() {
  const { selectedClientId } = useAppStore();

  return (
    <div className="flex-1 flex flex-col min-w-0 h-full">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto w-full px-6 py-8">
          {selectedClientId ? <ConversationThread /> : <MorningBriefing />}
        </div>
      </div>
      <InputBar />
    </div>
  );
}
