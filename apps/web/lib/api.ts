// Typed fetch wrapper for the Stage 2 FastAPI backend.
// HARD RESTRAINT (architecture § 5): do NOT replace with React Query / SWR /
// tRPC. If caching/retries become a real need, propose an ADR:
//   "ADR: introduce a client data-fetching layer for apps/web".

const DEFAULT_BASE = "http://localhost:8000";

function apiBase(): string {
  return process.env.NEXT_PUBLIC_API_BASE ?? DEFAULT_BASE;
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${apiBase()}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`GET ${url} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

export async function apiPost<T>(
  path: string,
  body: unknown,
  init?: RequestInit,
): Promise<T> {
  const url = `${apiBase()}${path}`;
  const res = await fetch(url, {
    method: "POST",
    ...init,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`POST ${url} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}
