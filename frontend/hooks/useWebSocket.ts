"use client";

import { useEffect, useRef, useCallback } from "react";
import { useAppStore } from "@/lib/store";
import type { AgentTask, ConversationMessage, TriTieredOutput, RagEntry } from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const {
    setWsConnected,
    addAgentTask,
    updateAgentTask,
    addMessage,
    setIsThinking,
    setThinkingStep,
    setThinkingAgent,
    setCurrentAnalysis,
    setCurrentTaskId,
    setArtifactOpen,
    alerts,
    setAlerts,
    clientDetail,
    setClientDetail,
  } = useAppStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
      reconnectTimer.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleMessage(msg);
      } catch {
        // ignore malformed messages
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleMessage = useCallback((msg: Record<string, unknown>) => {
    const type = msg.type as string;
    const payload = msg.payload as Record<string, unknown> || {};
    const msgClientId = msg.client_id as string | undefined;
    const currentClientId = useAppStore.getState().selectedClientId;
    const isForCurrentClient = !msgClientId || msgClientId === currentClientId;

    switch (type) {
      case "agent_dispatch": {
        if (!isForCurrentClient) break;
        const description = (payload.description as string) || "";
        addAgentTask({
          id: msg.task_id as string,
          client_id: msg.client_id as string,
          agent_type: msg.agent as string,
          status: "running",
          input_data: {},
          output_data: {},
          advisor_action: null,
          advisor_note: "",
          created_at: new Date().toISOString(),
          completed_at: null,
        });
        setThinkingAgent(msg.agent as string, "running", description);
        break;
      }
      case "agent_update": {
        if (!isForCurrentClient) break;
        updateAgentTask(msg.task_id as string, {
          status: "running",
          output_data: payload,
        });
        setThinkingAgent(msg.agent as string, "running");
        break;
      }
      case "agent_complete": {
        if (!isForCurrentClient) break;
        updateAgentTask(msg.task_id as string, {
          status: "completed",
          output_data: payload,
          completed_at: new Date().toISOString(),
        });
        setThinkingAgent(msg.agent as string, "completed");
        break;
      }
      case "chat_response": {
        if (!isForCurrentClient) break;
        setIsThinking(false);
        const newMsg: ConversationMessage = {
          id: crypto.randomUUID(),
          role: "shadow",
          content: payload.content as string,
          timestamp: new Date().toISOString(),
          task_id: msg.task_id as string | undefined,
        };
        if (payload.analysis) {
          newMsg.analysis = payload.analysis as TriTieredOutput;
        } else {
          setArtifactOpen(false);
        }
        addMessage(newMsg);
        break;
      }
      case "tri_tiered_output": {
        if (!isForCurrentClient) break;
        const analysis = payload as unknown as TriTieredOutput;
        setCurrentAnalysis(analysis);
        setCurrentTaskId(msg.task_id as string);
        setArtifactOpen(true);
        break;
      }
      case "thinking": {
        if (!isForCurrentClient) break;
        setIsThinking(true);
        if (payload.step) {
          setThinkingStep(payload.step as string);
        }
        break;
      }
      case "alert_new": {
        const newAlert = payload as unknown as Record<string, unknown>;
        setAlerts([...(alerts || []), newAlert as never]);
        break;
      }
      case "rag_updated": {
        if (!isForCurrentClient) break;
        const currentDetail = useAppStore.getState().clientDetail;
        const newEntries = (payload.entries as RagEntry[]) || [];
        if (currentDetail && newEntries.length > 0) {
          setClientDetail({
            ...currentDetail,
            rag_entries: [...(currentDetail.rag_entries || []), ...newEntries],
          });
        }
        break;
      }
      case "rag_deleted": {
        if (!isForCurrentClient) break;
        const detail = useAppStore.getState().clientDetail;
        const deletedIds = (payload.entry_ids as string[]) || [];
        if (detail && deletedIds.length > 0) {
          setClientDetail({
            ...detail,
            rag_entries: (detail.rag_entries || []).filter(
              (e) => !deletedIds.includes(e.id)
            ),
          });
        }
        break;
      }
      case "error": {
        if (!isForCurrentClient) break;
        setIsThinking(false);
        addMessage({
          id: crypto.randomUUID(),
          role: "shadow",
          content: (payload.message as string) || "Something went wrong. Please try again.",
          timestamp: new Date().toISOString(),
        });
        break;
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendMessage = useCallback((data: Record<string, unknown>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { sendMessage };
}
