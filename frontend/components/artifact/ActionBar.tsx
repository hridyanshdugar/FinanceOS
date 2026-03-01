"use client";

import { useState } from "react";
import { Check, Pencil, X } from "lucide-react";
import { toast } from "sonner";
import { useAppStore } from "@/lib/store";
import { api } from "@/lib/api";

export function ActionBar() {
  const { currentTaskId, setArtifactOpen, setCurrentAnalysis } = useAppStore();
  const [note, setNote] = useState("");
  const [acting, setActing] = useState(false);

  const handleAction = async (action: string) => {
    if (!currentTaskId || acting) return;
    setActing(true);
    try {
      await api.actOnTask(currentTaskId, action, note);
      if (action === "approved") {
        toast.success("Email sent successfully");
      }
      setArtifactOpen(false);
      setCurrentAnalysis(null);
    } catch {
      // silently handle
    } finally {
      setActing(false);
    }
  };

  return (
    <div className="border-t border-border px-5 py-4 space-y-3">
      <input
        type="text"
        placeholder="Add a note for your records (optional)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        className="w-full px-3 py-2 rounded-xl text-xs bg-background border border-border
                 placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/20"
      />
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleAction("approved")}
          disabled={acting}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
                   bg-primary text-primary-foreground text-sm font-medium
                   hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          <Check className="h-4 w-4" />
          Looks good, send it
        </button>
        <button
          onClick={() => handleAction("edited")}
          disabled={acting}
          className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl
                   border border-border text-sm font-medium text-foreground
                   hover:bg-accent transition-colors disabled:opacity-50"
        >
          <Pencil className="h-3.5 w-3.5" />
          Edit
        </button>
        <button
          onClick={() => handleAction("rejected")}
          disabled={acting}
          className="flex items-center justify-center px-3 py-2.5 rounded-xl
                   text-sm text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
