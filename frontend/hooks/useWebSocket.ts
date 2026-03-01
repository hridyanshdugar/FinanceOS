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

    switch (type) {
      case "agent_dispatch": {
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
        updateAgentTask(msg.task_id as string, {
          status: "running",
          output_data: payload,
        });
        setThinkingAgent(msg.agent as string, "running");
        break;
      }
      case "agent_complete": {
        updateAgentTask(msg.task_id as string, {
          status: "completed",
          output_data: payload,
          completed_at: new Date().toISOString(),
        });
        setThinkingAgent(msg.agent as string, "completed");
        break;
      }
      case "chat_response": {
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
        const analysis = payload as unknown as TriTieredOutput;
        setCurrentAnalysis(analysis);
        setCurrentTaskId(msg.task_id as string);
        setArtifactOpen(true);
        break;
      }
      case "thinking": {
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
        const newEntries = (payload.entries as RagEntry[]) || [];
        if (clientDetail && newEntries.length > 0) {
          setClientDetail({
            ...clientDetail,
            rag_entries: [...(clientDetail.rag_entries || []), ...newEntries],
          });
        }
        break;
      }
      case "rag_deleted": {
        const deletedIds = (payload.entry_ids as string[]) || [];
        if (clientDetail && deletedIds.length > 0) {
          setClientDetail({
            ...clientDetail,
            rag_entries: (clientDetail.rag_entries || []).filter(
              (e) => !deletedIds.includes(e.id)
            ),
          });
        }
        break;
      }
      case "error": {
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
