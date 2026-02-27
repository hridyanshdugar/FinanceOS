"use client";

import { Wifi, WifiOff } from "lucide-react";
import { useAppStore } from "@/lib/store";

export function ConnectionStatus() {
  const { wsConnected } = useAppStore();

  return (
    <div className="flex items-center gap-1.5 px-2 py-1">
      {wsConnected ? (
        <>
          <Wifi className="h-3 w-3 text-emerald-500" />
          <span className="text-[10px] text-muted-foreground">Connected</span>
        </>
      ) : (
        <>
          <WifiOff className="h-3 w-3 text-destructive" />
          <span className="text-[10px] text-destructive">Reconnecting...</span>
        </>
      )}
    </div>
  );
}
