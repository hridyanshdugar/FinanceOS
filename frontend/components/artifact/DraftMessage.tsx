"use client";

import { useState } from "react";
import { Mail, Pencil } from "lucide-react";

interface DraftMessageProps {
  data: {
    to: string;
    subject: string;
    body: string;
    tone: string;
    rag_highlights: string[];
  };
}

export function DraftMessage({ data }: DraftMessageProps) {
  const [editing, setEditing] = useState(false);
  const [body, setBody] = useState(data.body);

  return (
    <div className="rounded-2xl border border-border bg-background p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
            <Mail className="h-3.5 w-3.5" />
          </div>
          <h4 className="text-sm font-semibold text-foreground">Draft Message</h4>
        </div>
        <span className="text-[11px] px-2 py-0.5 rounded-full bg-purple-50 text-purple-600 font-medium">
          {data.tone}
        </span>
      </div>

      <div className="mb-3 space-y-1">
        <p className="text-xs text-muted-foreground">
          To: <span className="text-foreground">{data.to}</span>
        </p>
        <p className="text-xs text-muted-foreground">
          Subject: <span className="text-foreground">{data.subject}</span>
        </p>
      </div>

      {editing ? (
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          className="w-full min-h-[120px] p-3 rounded-xl bg-muted text-sm text-foreground
                   border border-border focus:outline-none focus:ring-2 focus:ring-primary/20
                   resize-y leading-relaxed"
        />
      ) : (
        <div className="p-3 rounded-xl bg-muted text-sm text-foreground leading-relaxed whitespace-pre-wrap">
          {body}
        </div>
      )}

      <button
        onClick={() => setEditing(!editing)}
        className="mt-2 flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
      >
        <Pencil className="h-3 w-3" />
        {editing ? "Done editing" : "Edit draft"}
      </button>

      {data.rag_highlights.length > 0 && (
        <div className="mt-3 text-[10px] text-muted-foreground">
          <span className="font-medium">Personalized with:</span>{" "}
          {data.rag_highlights.join(" · ")}
        </div>
      )}
    </div>
  );
}
