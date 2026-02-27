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
  clearClientChat: (id: string) => fetchJSON<Record<string, unknown>>(`/api/clients/${id}/chat`, { method: "DELETE" }),
  getAlerts: (status = "pending") => fetchJSON<Record<string, unknown>[]>(`/api/alerts?status=${status}`),
  actOnTask: (taskId: string, action: string, note = "") =>
    fetchJSON<Record<string, unknown>>(`/api/agents/tasks/${taskId}/action`, {
      method: "POST",
      body: JSON.stringify({ task_id: taskId, action, note }),
    }),
  addClientRag: (clientId: string, content: string) =>
    fetchJSON<Record<string, unknown>>(`/api/clients/${clientId}/rag`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),
  deleteClientRag: (clientId: string, entryId: string) =>
    fetchJSON<Record<string, unknown>>(`/api/clients/${clientId}/rag/${entryId}`, {
      method: "DELETE",
    }),
};
