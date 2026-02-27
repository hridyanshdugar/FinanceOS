const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  getClients: () => fetchJSON<Record<string, unknown>[]>("/api/clients"),
  getClient: (id: string) => fetchJSON<Record<string, unknown>>(`/api/clients/${id}`),
  getClientAccounts: (id: string) => fetchJSON<Record<string, unknown>[]>(`/api/clients/${id}/accounts`),
  getClientChat: (id: string) => fetchJSON<Record<string, unknown>[]>(`/api/clients/${id}/chat`),
  getAlerts: (status = "pending") => fetchJSON<Record<string, unknown>[]>(`/api/alerts?status=${status}`),
  actOnAlert: (alertId: string, action: string, note = "") =>
    fetchJSON<Record<string, unknown>>(`/api/alerts/${alertId}/action`, {
      method: "POST",
      body: JSON.stringify({ action, note }),
    }),
  getAgentTasks: (params?: { status?: string; client_id?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.client_id) searchParams.set("client_id", params.client_id);
    if (params?.limit) searchParams.set("limit", String(params.limit));
    return fetchJSON<Record<string, unknown>[]>(`/api/agents/tasks?${searchParams}`);
  },
  actOnTask: (taskId: string, action: string, note = "", editedContent?: string) =>
    fetchJSON<Record<string, unknown>>(`/api/agents/tasks/${taskId}/action`, {
      method: "POST",
      body: JSON.stringify({ task_id: taskId, action, note, edited_content: editedContent }),
    }),
  sendMessage: (clientId: string, content: string) =>
    fetchJSON<Record<string, unknown>>("/api/chat/send", {
      method: "POST",
      body: JSON.stringify({ client_id: clientId, content }),
    }),
};
