import { fallbackCollections, fallbackMetrics, fallbackScoreboard } from "@/lib/fallback-data";
import type { CollectionResponse, Entity, EntityType, MetricValue, RealityIndexItem, Scoreboard } from "@/types/api";

const API_BASE_URL = process.env.WEB_PUBLIC_API_BASE_URL ?? process.env.APIP_API_BASE_URL;
const PUBLIC_API_KEY = process.env.APIP_PUBLIC_API_KEY ?? process.env.WEB_PUBLIC_API_KEY;

async function apiFetch<T>(path: string, fallback: T): Promise<T> {
  if (!API_BASE_URL || !PUBLIC_API_KEY) {
    return fallback;
  }
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/${path}`, {
      headers: { "X-API-Key": PUBLIC_API_KEY },
      next: { revalidate: 60 }
    });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function adminProxyFetch(path: string, init: RequestInit = {}) {
  if (!API_BASE_URL) {
    return Response.json(
      { code: "api_unavailable", message: "APIP_API_BASE_URL is not configured." },
      { status: 503 }
    );
  }
  const headers = new Headers(init.headers);
  const authorization = headers.get("Authorization");
  if (!authorization?.startsWith("Bearer ")) {
    return Response.json(
      { code: "admin_auth_required", message: "Admin login is required." },
      { status: 401 }
    );
  }
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });
  const body = await response.text();
  return new Response(body, {
    status: response.status,
    headers: { "Content-Type": response.headers.get("Content-Type") ?? "application/json" }
  });
}

export function fetchScoreboard() {
  return apiFetch<Scoreboard>("scoreboard", fallbackScoreboard);
}

export function fetchRealityIndex(entityType?: EntityType) {
  const suffix = entityType ? `?entity_type=${entityType}` : "";
  return apiFetch<CollectionResponse<RealityIndexItem>>("ai-reality-index" + suffix, {
    items: fallbackScoreboard.top_ai_reality_index.filter((item) =>
      entityType ? item.entity_type === entityType : true
    ),
    next_cursor: null
  });
}

export function fetchCollection(resource: "companies" | "industries" | "countries" | "models") {
  return apiFetch<CollectionResponse<Entity>>(resource, fallbackCollections[resource]);
}

export async function fetchEntity(resource: "companies" | "industries" | "countries" | "models", id: string) {
  const collection = fallbackCollections[resource];
  const fallback = collection.items.find((item) => item.id === id) ?? collection.items[0];
  return apiFetch<Entity>(`${resource}/${id}`, {
    ...fallback,
    metrics: fallbackMetrics.filter((metric) => metric.entity_id === fallback.id)
  });
}

export function fetchMetrics() {
  return apiFetch<CollectionResponse<MetricValue>>("metrics/search", {
    items: fallbackMetrics,
    next_cursor: null
  });
}
