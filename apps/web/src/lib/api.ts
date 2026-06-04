import { fallbackCollections, fallbackMetrics, fallbackScoreboard } from "@/lib/fallback-data";
import type { CollectionResponse, Entity, EntityType, MetricValue, Scoreboard } from "@/types/api";

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

export function fetchScoreboard() {
  return apiFetch<Scoreboard>("scoreboard", fallbackScoreboard);
}

export function fetchRealityIndex(entityType?: EntityType) {
  const suffix = entityType ? `?entity_type=${entityType}` : "";
  return apiFetch<CollectionResponse>("ai-reality-index" + suffix, {
    items: fallbackScoreboard.top_ai_reality_index.map((item) => ({
      id: item.entity_id,
      name: labelForEntity(item.entity_id),
      metrics: [
        {
          id: `${item.entity_id}_reality_index`,
          metric_key: "ai_reality_index",
          entity_type: item.entity_type,
          entity_id: item.entity_id,
          value: item.score,
          unit: "score",
          period_start: "2026-01-01",
          period_end: "2026-12-31",
          confidence: fallbackScoreboard.confidence
        }
      ]
    })),
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

function labelForEntity(entityId: string) {
  const allEntities = Object.values(fallbackCollections).flatMap((collection) => collection.items);
  return allEntities.find((entity) => entity.id === entityId)?.name ?? entityId.replaceAll("_", " ");
}
