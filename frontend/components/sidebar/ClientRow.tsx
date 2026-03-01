"use client";

import type { Client } from "@/lib/types";
import { cn } from "@/lib/utils";

const AVATAR_COLORS = [
  "bg-amber-100 text-amber-700",
  "bg-emerald-100 text-emerald-700",
  "bg-blue-100 text-blue-700",
  "bg-purple-100 text-purple-700",
  "bg-rose-100 text-rose-700",
  "bg-teal-100 text-teal-700",
  "bg-indigo-100 text-indigo-700",
  "bg-orange-100 text-orange-700",
];

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function getColorIndex(name: string): number {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % AVATAR_COLORS.length;
}

interface ClientRowProps {
  client: Client;
  isActive: boolean;
  onClick: () => void;
}

export function ClientRow({ client, isActive, onClick }: ClientRowProps) {
  const initials = getInitials(client.name);
  const colorClass = AVATAR_COLORS[getColorIndex(client.name)];
  const hasPendingRequests = (client.pending_requests ?? 0) > 0;

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all duration-150",
        isActive
          ? "bg-accent"
          : "hover:bg-accent/50"
      )}
    >
      <div className={cn("h-8 w-8 rounded-full flex items-center justify-center text-xs font-medium shrink-0", colorClass)}>
        {initials}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground truncate">{client.name}</p>
        <p className="text-[11px] text-muted-foreground truncate">
          {client.province} · {client.risk_profile}
        </p>
      </div>
      {hasPendingRequests && (
        <span className="h-2 w-2 rounded-full bg-amber-500 shrink-0" />
      )}
    </button>
  );
}
