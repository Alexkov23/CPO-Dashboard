import type {
  DashboardMetrics,
  Source,
  SourceCreate,
  SyncResult,
  TasksGroupedByDate,
} from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  getSources: () => request<Source[]>("/api/sources"),

  createSource: (data: SourceCreate) =>
    request<Source>("/api/sources", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  toggleSource: (id: string, enabled: boolean) =>
    request<Source>(`/api/sources/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ enabled }),
    }),

  deleteSource: (id: string) =>
    request<void>(`/api/sources/${id}`, { method: "DELETE" }),

  getTasks: (project?: string) => {
    const params = project ? `?project=${encodeURIComponent(project)}` : "";
    return request<TasksGroupedByDate[]>(`/api/tasks${params}`);
  },

  getProjects: () => request<string[]>("/api/projects"),

  getMetrics: (project?: string) => {
    const params = project ? `?project=${encodeURIComponent(project)}` : "";
    return request<DashboardMetrics>(`/api/metrics${params}`);
  },

  syncAll: () => request<SyncResult[]>("/api/sync", { method: "POST" }),

  syncSource: (id: string) =>
    request<SyncResult>(`/api/sync/${id}`, { method: "POST" }),
};
