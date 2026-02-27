"use client";

import { useEffect, useRef, useCallback } from "react";
import { useAppStore } from "@/lib/store";
import type { AgentTask, ConversationMessage, TriTieredOutput } from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const {
    setWsConnected,
    addAgentTask,
    updateAgentTask,
    addMessage,
    updateMessage,
    setIsThinking,
    setCurrentAnalysis,
    setCurrentTaskId,
    setArtifactOpen,
    alerts,
    setAlerts,
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
        break;
      }
      case "agent_update": {
        updateAgentTask(msg.task_id as string, {
          status: "running",
          output_data: payload,
        });
        break;
      }
      case "agent_complete": {
        updateAgentTask(msg.task_id as string, {
          status: "completed",
          output_data: payload,
          completed_at: new Date().toISOString(),
        });
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
        break;
      }
      case "alert_new": {
        const newAlert = payload as unknown as Record<string, unknown>;
        setAlerts([...(alerts || []), newAlert as never]);
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
