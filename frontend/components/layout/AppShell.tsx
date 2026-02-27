"use client";

import { useEffect } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { MainArea } from "@/components/conversation/MainArea";
import { ArtifactPanel } from "@/components/artifact/ArtifactPanel";
import { useAppStore } from "@/lib/store";
import { useWebSocket } from "@/hooks/useWebSocket";
import { api } from "@/lib/api";
import type { Client, Alert } from "@/lib/types";

export function AppShell() {
  const { setClients, setAlerts, artifactOpen } = useAppStore();
  const { sendMessage } = useWebSocket();

  useEffect(() => {
    api.getClients().then((data) => setClients(data as unknown as Client[]));
    api.getAlerts().then((data) => setAlerts(data as unknown as Alert[]));
  }, [setClients, setAlerts]);

  return (
    <WsSendContext.Provider value={sendMessage}>
      <div className="flex h-screen w-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex-1 flex min-w-0">
          <MainArea />
          {artifactOpen && <ArtifactPanel />}
        </main>
      </div>
    </WsSendContext.Provider>
  );
}

import { createContext, useContext } from "react";

type SendFn = (data: Record<string, unknown>) => void;
const WsSendContext = createContext<SendFn>(() => {});
export const useWsSend = () => useContext(WsSendContext);
