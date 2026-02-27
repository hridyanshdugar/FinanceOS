import { create } from "zustand";
import type {
  Client,
  Alert,
  AgentTask,
  ConversationMessage,
  TriTieredOutput,
  ClientDetail,
} from "./types";

type ActivePanel = "overview" | "chat" | null;

interface AppState {
  clients: Client[];
  setClients: (clients: Client[]) => void;

  selectedClientId: string | null;
  setSelectedClientId: (id: string | null) => void;

  clientDetail: ClientDetail | null;
  setClientDetail: (detail: ClientDetail | null) => void;

  alerts: Alert[];
  setAlerts: (alerts: Alert[]) => void;
  removeAlert: (id: string) => void;

  agentTasks: AgentTask[];
  setAgentTasks: (tasks: AgentTask[]) => void;
  addAgentTask: (task: AgentTask) => void;
  updateAgentTask: (taskId: string, updates: Partial<AgentTask>) => void;

  conversation: ConversationMessage[];
  setConversation: (messages: ConversationMessage[]) => void;
  addMessage: (message: ConversationMessage) => void;
  updateMessage: (id: string, updates: Partial<ConversationMessage>) => void;

  artifactOpen: boolean;
  setArtifactOpen: (open: boolean) => void;

  currentAnalysis: TriTieredOutput | null;
  setCurrentAnalysis: (analysis: TriTieredOutput | null) => void;
  currentTaskId: string | null;
  setCurrentTaskId: (id: string | null) => void;

  isThinking: boolean;
  setIsThinking: (thinking: boolean) => void;

  thinkingStep: string;
  setThinkingStep: (step: string) => void;

  thinkingAgents: Record<string, { status: string; description: string }>;
  setThinkingAgent: (agent: string, status: string, description?: string) => void;
  clearThinkingAgents: () => void;

  wsConnected: boolean;
  setWsConnected: (connected: boolean) => void;

  activePanel: ActivePanel;
  setActivePanel: (panel: ActivePanel) => void;
}

export const useAppStore = create<AppState>((set) => ({
  clients: [],
  setClients: (clients) => set({ clients }),

  selectedClientId: null,
  setSelectedClientId: (id) =>
    set({
      selectedClientId: id,
      conversation: [],
      artifactOpen: false,
      currentAnalysis: null,
      activePanel: id ? "overview" : null,
    }),

  clientDetail: null,
  setClientDetail: (detail) => set({ clientDetail: detail }),

  alerts: [],
  setAlerts: (alerts) => set({ alerts }),
  removeAlert: (id) => set((s) => ({ alerts: s.alerts.filter((a) => a.id !== id) })),

  agentTasks: [],
  setAgentTasks: (tasks) => set({ agentTasks: tasks }),
  addAgentTask: (task) => set((s) => ({ agentTasks: [task, ...s.agentTasks].slice(0, 20) })),
  updateAgentTask: (taskId, updates) =>
    set((s) => ({
      agentTasks: s.agentTasks.map((t) => (t.id === taskId ? { ...t, ...updates } : t)),
    })),

  conversation: [],
  setConversation: (messages) => set({ conversation: messages }),
  addMessage: (message) => set((s) => ({ conversation: [...s.conversation, message] })),
  updateMessage: (id, updates) =>
    set((s) => ({
      conversation: s.conversation.map((m) => (m.id === id ? { ...m, ...updates } : m)),
    })),

  artifactOpen: false,
  setArtifactOpen: (open) => set({ artifactOpen: open }),

  currentAnalysis: null,
  setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),
  currentTaskId: null,
  setCurrentTaskId: (id) => set({ currentTaskId: id }),

  isThinking: false,
  setIsThinking: (thinking) => set({
    isThinking: thinking,
    thinkingAgents: {},
    thinkingStep: thinking ? "Analyzing your question..." : "",
  }),

  thinkingStep: "",
  setThinkingStep: (step) => set({ thinkingStep: step }),

  thinkingAgents: {},
  setThinkingAgent: (agent, status, description) =>
    set((s) => ({
      thinkingAgents: {
        ...s.thinkingAgents,
        [agent]: { status, description: description || s.thinkingAgents[agent]?.description || "" },
      },
    })),
  clearThinkingAgents: () => set({ thinkingAgents: {}, thinkingStep: "" }),

  wsConnected: false,
  setWsConnected: (connected) => set({ wsConnected: connected }),

  activePanel: null,
  setActivePanel: (panel) => set({ activePanel: panel }),
}));
