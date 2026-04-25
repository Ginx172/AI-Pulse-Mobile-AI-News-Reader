const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Article {
  id: string | number;
  title: string;
  url?: string;
  source?: string;
  author?: string;
  published_at?: string;
  summary?: string;
  score?: number;
}

export interface Source {
  id: string;
  name: string;
  url?: string;
  type?: string;
  active: boolean;
  is_custom?: boolean;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function getArticlesToday(): Promise<Article[]> {
  return apiFetch<Article[]>("/articles/today");
}

export async function getArticle(id: string | number): Promise<Article> {
  return apiFetch<Article>(`/articles/${id}`);
}

export async function getSources(): Promise<Source[]> {
  return apiFetch<Source[]>("/sources");
}

export async function toggleSource(id: string): Promise<Source> {
  return apiFetch<Source>(`/sources/${id}/toggle`, { method: "POST" });
}

export async function addCustomSource(
  name: string,
  url: string,
  type: string
): Promise<Source> {
  return apiFetch<Source>("/sources/custom", {
    method: "POST",
    body: JSON.stringify({ name, url, type }),
  });
}

export async function deleteCustomSource(id: string): Promise<void> {
  await apiFetch(`/sources/custom/${id}`, { method: "DELETE" });
}
