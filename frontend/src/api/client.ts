import type { Api, ProjectCreate } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers }
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "请求失败");
  }
  return response.json() as Promise<T>;
}

export const api: Api = {
  createProject(input: ProjectCreate) {
    return request("/projects", { method: "POST", body: JSON.stringify(input) });
  },
  listProjects() {
    return request("/projects");
  },
  importFixture(projectId: string) {
    return request(`/projects/${projectId}/collections/fixture`, { method: "POST" });
  },
  importXiaohongshu(projectId: string, keyword: string) {
    return request(`/projects/${projectId}/collections/xiaohongshu?keyword=${encodeURIComponent(keyword)}`, { method: "POST" });
  },
  listNotes(projectId: string) {
    return request(`/projects/${projectId}/notes`);
  },
  listCollectionRuns(projectId: string) {
    return request(`/projects/${projectId}/collections`);
  },
  rankNotes(projectId: string) {
    return request(`/projects/${projectId}/analysis/rank`, { method: "POST" });
  },
  createTopic(projectId: string, input: Record<string, string>) {
    return request(`/projects/${projectId}/topics`, { method: "POST", body: JSON.stringify(input) });
  },
  generateDrafts(topicId: string) {
    return request(`/topics/${topicId}/drafts/generate`, { method: "POST" });
  },
  runVerticalResearch(projectId: string, topic: string) {
    return request(`/projects/${projectId}/analysis/research?topic=${encodeURIComponent(topic)}`, { method: "POST" });
  }
};
