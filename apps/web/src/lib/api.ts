import { fallbackCollections, fallbackMetrics, fallbackScoreboard } from "@/lib/fallback-data";
import type { CollectionResponse, Entity, EntityType, MetricValue, RealityIndexItem, Scoreboard } from "@/types/api";

const API_BASE_URL = process.env.WEB_PUBLIC_API_BASE_URL ?? process.env.APIP_API_BASE_URL;
const LOGIN_EMAIL = process.env.APIP_DEMO_EMAIL ?? "admin@openvalidations.com";
const LOGIN_PASSWORD = process.env.APIP_DEMO_PASSWORD ?? "apip-admin-change-me";

let cachedToken: string | null = null;

async function getToken() {
  if (!API_BASE_URL) {
    return null;
  }
  if (cachedToken) {
    return cachedToken;
  }
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: LOGIN_EMAIL, password: LOGIN_PASSWORD }),
      cache: "no-store"
    });
    if (!response.ok) {
      return null;
    }
    const data = (await response.json()) as { access_token: string };
    cachedToken = data.access_token;
    return cachedToken;
  } catch {
    return null;
  }
}

async function apiFetch<T>(path: string, fallback: T): Promise<T> {
  if (!API_BASE_URL) {
    return fallback;
  }
  const token = await getToken();
  if (!token) {
    return fallback;
  }
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/${path}`, {
      headers: { Authorization: `Bearer ${token}` },
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
  const token = await getToken();
  if (!token) {
    return Response.json(
      { code: "admin_auth_unavailable", message: "Unable to authenticate admin API session." },
      { status: 401 }
    );
  }
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);
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
