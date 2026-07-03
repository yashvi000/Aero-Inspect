/**
 * Thin client-side API wrapper. Currently a stub — the demo workflow is driven
 * by in-memory Zustand stores under `@/web/hooks`. Wire real endpoints here
 * when the backend under `src/backend` comes online.
 */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!res.ok) throw new Error(`API ${path} failed: ${res.status}`);
  return (await res.json()) as T;
}
