import { fallbackCollections, fallbackMetrics, fallbackScoreboard } from "@/lib/fallback-data";
import type {
  CollectionResponse,
  AutonomousEvidenceRecord,
  CompanyOpenValsScore,
  Entity,
  EntityType,
  MetricValue,
  MicrosoftValidationReport,
  RealityIndexItem,
  Scoreboard,
  SourceLineage,
  TrustCenter,
  TrustIndexDashboard,
  TrustIndexItem
} from "@/types/api";

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

const fallbackTrustIndex: TrustIndexItem = {
  entity_type: "global",
  entity_id: null,
  entity_name: "APIP Global Trust Index",
  trust_index: 0,
  trust_rating: "Low Trust",
  trust_classification: "Insufficient Evidence",
  components: {
    confidence: 0,
    evidence_coverage: 0,
    transparency: 0,
    reproducibility: 0,
    source_quality: 0
  },
  weights: {
    confidence: 0.3,
    evidence_coverage: 0.25,
    transparency: 0.2,
    reproducibility: 0.15,
    source_quality: 0.1
  },
  source_count: 0,
  published_record_count: 0,
  methodology_version: "trust-index-v1"
};

export function fetchTrustIndex() {
  return apiFetch<TrustIndexDashboard>("trust-index", {
    summary: fallbackTrustIndex,
    leaderboard: [],
    trend: [],
    notifications: [],
    methodology: {
      name: "OpenVals Trust Index",
      version: "trust-index-v1",
      formula:
        "30% Confidence + 25% Evidence Coverage + 20% Transparency + 15% Reproducibility + 10% Source Quality",
      weights: fallbackTrustIndex.weights,
      rating_scale: {
        "90-100": "Verified / Gold Standard",
        "80-89": "High Trust / Strong Evidence",
        "70-79": "Trusted / Reliable",
        "60-69": "Watchlist / Developing",
        "0-59": "Low Trust / Insufficient Evidence"
      }
    }
  });
}

export function fetchTrustLeaderboard() {
  return apiFetch<CollectionResponse<TrustIndexItem>>("leaderboard", {
    items: [],
    next_cursor: null
  });
}

export function fetchMicrosoftValidationReport() {
  return apiFetch<MicrosoftValidationReport>("companies/microsoft/validation-report", {
    id: "microsoft-validation-fallback",
    company: "Microsoft",
    company_slug: "microsoft",
    status: "in_progress",
    gold_standard_rank: null,
    gold_standard_label: null,
    report_path: "/companies/microsoft/validation-report",
    methodology_version: "gold-standard-v1",
    methodology_trace:
      "Gold Standard v1 validates Microsoft through required evidence sections, source approval, lineage, reviewer notes, and methodology traceability.",
    reviewer_notes: "Configure the backend API to load the live Microsoft validation workspace.",
    evidence_coverage_score: 0,
    openvals_validation_score: 0,
    openvals_validation_label: "Insufficient Evidence",
    exported_at: null,
    last_updated: null,
    sections: [],
    source_lineage: []
  });
}

export function fetchNvidiaValidationReport() {
  return apiFetch<MicrosoftValidationReport>("companies/nvidia/validation-report", {
    id: "nvidia-validation-fallback",
    company: "NVIDIA",
    company_slug: "nvidia",
    status: "in_progress",
    gold_standard_rank: null,
    gold_standard_label: null,
    report_path: "/companies/nvidia/validation-report",
    methodology_version: "gold-standard-v1",
    methodology_trace:
      "Gold Standard v1 validates NVIDIA through required evidence sections, source approval, lineage, reviewer notes, and methodology traceability.",
    reviewer_notes: "Configure the backend API to load the live NVIDIA validation workspace.",
    evidence_coverage_score: 0,
    openvals_validation_score: 0,
    openvals_validation_label: "Insufficient Evidence",
    exported_at: null,
    last_updated: null,
    sections: [],
    source_lineage: []
  });
}

export function fetchAlphabetValidationReport() {
  return apiFetch<MicrosoftValidationReport>("companies/alphabet/validation-report", {
    id: "alphabet-validation-fallback",
    company: "Alphabet",
    company_slug: "alphabet",
    status: "in_progress",
    gold_standard_rank: null,
    gold_standard_label: null,
    report_path: "/companies/alphabet/validation-report",
    methodology_version: "gold-standard-v1",
    methodology_trace:
      "Gold Standard v1 validates Alphabet through required evidence sections, source approval, lineage, reviewer notes, and methodology traceability.",
    reviewer_notes: "Configure the backend API to load the live Alphabet validation workspace.",
    evidence_coverage_score: 0,
    openvals_validation_score: 0,
    openvals_validation_label: "Insufficient Evidence",
    exported_at: null,
    last_updated: null,
    sections: [],
    source_lineage: []
  });
}

export function fetchTrustCenter() {
  return apiFetch<TrustCenter>("trust-center", {
    workflow: "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH",
    auto_publish_enabled: false,
    metrics: {
      total_records: 0,
      published_records: 0,
      approved_records: 0,
      under_review_records: 0,
      manual_review_required: 0,
      average_confidence: 0,
      average_openvals_score: 0,
      public_lineage_records: 0
    },
    trust_index: fallbackTrustIndex,
    trust_trend: [],
    trust_notifications: [],
    methodology: {
      name: "OpenVals Trust Index",
      version: "trust-index-v1",
      formula:
        "30% Confidence + 25% Evidence Coverage + 20% Transparency + 15% Reproducibility + 10% Source Quality",
      weights: fallbackTrustIndex.weights,
      rating_scale: {
        "90-100": "Verified / Gold Standard",
        "80-89": "High Trust / Strong Evidence",
        "70-79": "Trusted / Reliable",
        "60-69": "Watchlist / Developing",
        "0-59": "Low Trust / Insufficient Evidence"
      }
    },
    items: []
  });
}

export function fetchMicrosoftEvidenceTimeline() {
  return apiFetch<CollectionResponse<AutonomousEvidenceRecord>>(
    "companies/microsoft/evidence-timeline",
    { items: [], next_cursor: null }
  );
}

export function fetchNvidiaEvidenceTimeline() {
  return apiFetch<CollectionResponse<AutonomousEvidenceRecord>>(
    "companies/nvidia/evidence-timeline",
    { items: [], next_cursor: null }
  );
}

export function fetchAlphabetEvidenceTimeline() {
  return apiFetch<CollectionResponse<AutonomousEvidenceRecord>>(
    "companies/alphabet/evidence-timeline",
    { items: [], next_cursor: null }
  );
}

export function fetchMicrosoftSourceLineage() {
  return apiFetch<{ company: string; items: SourceLineage[]; next_cursor: null }>(
    "companies/microsoft/source-lineage",
    { company: "Microsoft", items: [], next_cursor: null }
  );
}

export function fetchNvidiaSourceLineage() {
  return apiFetch<{ company: string; items: SourceLineage[]; next_cursor: null }>(
    "companies/nvidia/source-lineage",
    { company: "NVIDIA", items: [], next_cursor: null }
  );
}

export function fetchAlphabetSourceLineage() {
  return apiFetch<{ company: string; items: SourceLineage[]; next_cursor: null }>(
    "companies/alphabet/source-lineage",
    { company: "Alphabet", items: [], next_cursor: null }
  );
}

export function fetchMicrosoftOpenValsScore() {
  return apiFetch<CompanyOpenValsScore>("companies/microsoft/openvals-score", {
    company: "Microsoft",
    company_slug: "microsoft",
    gold_standard_rank: null,
    gold_standard_label: null,
    openvals_score: 0,
    classification: "Weak",
    published_records: 0,
    evidence_coverage_score: 0,
    confidence_score: 0,
    source_count: 0,
    last_updated: null,
    methodology_note: "Microsoft pilot validation data is not available yet."
  });
}

export function fetchNvidiaOpenValsScore() {
  return apiFetch<CompanyOpenValsScore>("companies/nvidia/openvals-score", {
    company: "NVIDIA",
    company_slug: "nvidia",
    gold_standard_rank: null,
    gold_standard_label: null,
    openvals_score: 0,
    classification: "Weak",
    published_records: 0,
    evidence_coverage_score: 0,
    confidence_score: 0,
    source_count: 0,
    last_updated: null,
    methodology_note: "NVIDIA Gold Standard validation data is not available yet."
  });
}

export function fetchAlphabetOpenValsScore() {
  return apiFetch<CompanyOpenValsScore>("companies/alphabet/openvals-score", {
    company: "Alphabet",
    company_slug: "alphabet",
    gold_standard_rank: null,
    gold_standard_label: null,
    openvals_score: 0,
    classification: "Weak",
    published_records: 0,
    evidence_coverage_score: 0,
    confidence_score: 0,
    source_count: 0,
    last_updated: null,
    methodology_note: "Alphabet Gold Standard validation data is not available yet."
  });
}

export function fetchMicrosoftTrustReport() {
  return apiFetch<TrustCenter>("companies/microsoft/trust-report", {
    company: "Microsoft",
    company_slug: "microsoft",
    status: "in_progress",
    gold_standard_rank: null,
    gold_standard_label: null,
    workflow: "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH",
    auto_publish_enabled: false,
    metrics: {
      total_records: 0,
      published_records: 0,
      approved_records: 0,
      under_review_records: 0,
      manual_review_required: 0,
      average_confidence: 0,
      average_openvals_score: 0,
      public_lineage_records: 0
    },
    items: []
  });
}

export function fetchNvidiaTrustReport() {
  return apiFetch<TrustCenter>("companies/nvidia/trust-report", {
    company: "NVIDIA",
    company_slug: "nvidia",
    status: "in_progress",
    gold_standard_rank: null,
    gold_standard_label: null,
    workflow: "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH",
    auto_publish_enabled: false,
    metrics: {
      total_records: 0,
      published_records: 0,
      approved_records: 0,
      under_review_records: 0,
      manual_review_required: 0,
      average_confidence: 0,
      average_openvals_score: 0,
      public_lineage_records: 0
    },
    items: []
  });
}

export function fetchAlphabetTrustReport() {
  return apiFetch<TrustCenter>("companies/alphabet/trust-report", {
    company: "Alphabet",
    company_slug: "alphabet",
    status: "in_progress",
    gold_standard_rank: null,
    gold_standard_label: null,
    workflow: "COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH",
    auto_publish_enabled: false,
    metrics: {
      total_records: 0,
      published_records: 0,
      approved_records: 0,
      under_review_records: 0,
      manual_review_required: 0,
      average_confidence: 0,
      average_openvals_score: 0,
      public_lineage_records: 0
    },
    items: []
  });
}
