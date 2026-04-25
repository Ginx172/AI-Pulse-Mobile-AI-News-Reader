/**
 * Backend API client for the Pulse AI web app.
 *
 * Base URL is taken from `NEXT_PUBLIC_API_URL` (set in `.env.local`),
 * falling back to `http://localhost:8000` for local development.
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Article {
  id: string;
  title: string;
  url?: string;
  source?: string;
  source_id?: string;
  author?: string;
  summary?: string;
  published_at?: string;
  rank?: number;
  score?: number;
  image_url?: string | null;
}

export interface Source {
  id: string;
  name: string;
  url?: string;
  rss_url?: string | null;
  category?: string;
  type?: string;
  language?: string;
  active: boolean;
  effective_weight?: number;
  weight_override?: number | null;
  is_custom?: boolean;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(
      `Request failed: ${res.status} ${res.statusText}${body ? ` — ${body}` : ""}`
    );
  }
  // Some endpoints (DELETE) may have empty bodies
  if (res.status === 204) return undefined as unknown as T;
  return (await res.json()) as T;
}

/* -------------------------------------------------------------------------- */
/* Articles                                                                    */
/* -------------------------------------------------------------------------- */

/** Today's top 25 ranked articles. */
export function getArticlesToday(): Promise<Article[]> {
  return request<Article[]>("/articles/today");
}

/** A single article by id. */
export function getArticle(id: string): Promise<Article> {
  return request<Article>(`/articles/${encodeURIComponent(id)}`);
}

/* -------------------------------------------------------------------------- */
/* Sources                                                                     */
/* -------------------------------------------------------------------------- */

/** All sources (official + custom) with active state and effective weight. */
export function getSources(): Promise<Source[]> {
  return request<Source[]>("/sources");
}

/**
 * Flip the `active` flag for a source. Returns the updated source.
 * Backend handles the toggle by inverting the current state.
 */
export async function toggleSource(id: string): Promise<Source> {
  // Resolve current state then patch — keeps the helper resilient even if
  // the backend doesn't expose a dedicated /toggle endpoint.
  const sources = await getSources();
  const current = sources.find((s) => s.id === id);
  const nextActive = !(current?.active ?? true);
  return request<Source>(`/sources/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: JSON.stringify({ active: nextActive }),
  });
}

/** Create a custom source. RSS is auto-discovered server-side when omitted. */
export function addCustomSource(
  name: string,
  url: string,
  type: string
): Promise<Source> {
  return request<Source>("/sources/custom", {
    method: "POST",
    body: JSON.stringify({ name, url, type }),
  });
}

/** Delete a user-added custom source. */
export function deleteCustomSource(id: string): Promise<void> {
  return request<void>(`/sources/custom/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}
