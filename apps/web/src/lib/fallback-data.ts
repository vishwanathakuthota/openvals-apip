import type { CollectionResponse, Entity, MetricValue, Scoreboard } from "@/types/api";

export const defaultConfidence = {
  score: 80,
  label: "High Confidence",
  source_count: 3,
  last_updated: "2026-06-04T09:00:00Z",
  source_reliability: 65,
  data_freshness: 90,
  cross_verification: 70,
  methodology_transparency: 75
};

export const fallbackCollections: Record<"companies" | "industries" | "countries" | "models", CollectionResponse> = {
  companies: {
    items: [
      { id: "company_openai", name: "OpenAI", slug: "openai", ticker: null, status: "active" },
      { id: "company_anthropic", name: "Anthropic", slug: "anthropic", ticker: null, status: "active" },
      { id: "company_google", name: "Google", slug: "google", ticker: "GOOGL", status: "active" },
      { id: "company_microsoft", name: "Microsoft", slug: "microsoft", ticker: "MSFT", status: "active" },
      { id: "company_meta", name: "Meta", slug: "meta", ticker: "META", status: "active" },
      { id: "company_amazon", name: "Amazon", slug: "amazon", ticker: "AMZN", status: "active" },
      { id: "company_nvidia", name: "NVIDIA", slug: "nvidia", ticker: "NVDA", status: "active" }
    ],
    next_cursor: null
  },
  industries: {
    items: [
      { id: "industry_healthcare", name: "Healthcare AI", slug: "healthcare-ai", status: "active" },
      { id: "industry_cybersecurity", name: "Cybersecurity AI", slug: "cybersecurity-ai", status: "active" },
      { id: "industry_finance", name: "Finance AI", slug: "finance-ai", status: "active" },
      { id: "industry_legal", name: "Legal AI", slug: "legal-ai", status: "active" }
    ],
    next_cursor: null
  },
  countries: {
    items: [
      { id: "country_us", name: "United States", slug: "united-states", iso_code: "US", region: "North America" },
      { id: "country_cn", name: "China", slug: "china", iso_code: "CN", region: "Asia" },
      { id: "country_in", name: "India", slug: "india", iso_code: "IN", region: "Asia" },
      { id: "country_gb", name: "United Kingdom", slug: "united-kingdom", iso_code: "GB", region: "Europe" }
    ],
    next_cursor: null
  },
  models: {
    items: [
      { id: "model_gpt", name: "GPT", slug: "gpt", model_family: "GPT", status: "active" },
      { id: "model_claude", name: "Claude", slug: "claude", model_family: "Claude", status: "active" },
      { id: "model_gemini", name: "Gemini", slug: "gemini", model_family: "Gemini", status: "active" },
      { id: "model_llama", name: "Llama", slug: "llama", model_family: "Llama", status: "active" }
    ],
    next_cursor: null
  }
};

export const fallbackMetrics: MetricValue[] = [
  metric("metric_openai_revenue_2026", "company", "company_openai", "ai_revenue", 12500000000, "usd"),
  metric("metric_openai_spend_2026", "company", "company_openai", "ai_spend", 16000000000, "usd"),
  metric("metric_us_revenue_2026", "country", "country_us", "ai_revenue", 165000000000, "usd"),
  metric("metric_healthcare_roi_2026", "industry", "industry_healthcare", "roi", 1.18, "ratio"),
  metric("metric_gpt_margin_2026", "model", "model_gpt", "gross_margin", 0.61, "ratio")
];

export const fallbackScoreboard: Scoreboard = {
  total_ai_spend: 420000000000,
  total_ai_revenue: 310000000000,
  net_profit: -110000000000,
  global_roi: 0.7381,
  profitability_gauge: "PARTIALLY",
  companies_tracked: 50,
  industries_tracked: 10,
  countries_tracked: 10,
  confidence: {
    ...defaultConfidence,
    score: 71.4,
    label: "Medium Confidence",
    source_count: 184,
    methodology_note:
      "Global dashboard confidence reflects approved metric records and source coverage across APIP seed data."
  },
  top_ai_reality_index: [
    reality("company", "company_nvidia", "NVIDIA", 88.9, "Strong", 94, 88, 74, 91),
    reality("company", "company_openai", "OpenAI", 72.2, "Strong", 78, 82, 48, 76),
    reality("industry", "industry_healthcare", "Healthcare AI", 86.4, "Strong", 100, 59, 62, 67),
    reality("country", "country_us", "United States", 67.7, "Emerging", 74, 68, 45, 61)
  ]
};

export function entityName(entityId: string) {
  const allEntities: Entity[] = Object.values(fallbackCollections).flatMap((collection) => collection.items);
  return allEntities.find((entity) => entity.id === entityId)?.name ?? entityId.replaceAll("_", " ");
}

function metric(
  id: string,
  entity_type: MetricValue["entity_type"],
  entity_id: string,
  metric_key: string,
  value: number,
  unit: string
): MetricValue {
  return {
    id,
    entity_type,
    entity_id,
    metric_key,
    value,
    confidence_score: defaultConfidence.score,
    confidence_label: defaultConfidence.label,
    source_count: defaultConfidence.source_count,
    last_updated: defaultConfidence.last_updated,
    methodology_note: "Synthetic APIP baseline calculated from approved source records.",
    unit,
    period_start: "2026-01-01",
    period_end: "2026-12-31",
    methodology: "Synthetic APIP backend seed baseline.",
    confidence: defaultConfidence,
    sources: [
      {
        id: "src_synthetic_annual_report",
        title: "Synthetic APIP Annual Report Baseline",
        source_type: "annual_report",
        publisher: "OpenVals",
        url: "https://example.com/apip-annual-report",
        published_at: "2026-05-20T00:00:00Z",
        reliability_score: 95,
        evidence_note: "Fallback source transparency record."
      },
      {
        id: "src_synthetic_investor_presentation",
        title: "Synthetic APIP Investor Presentation",
        source_type: "investor_presentation",
        publisher: "OpenVals",
        url: "https://example.com/apip-investor-presentation",
        published_at: "2026-04-15T00:00:00Z",
        reliability_score: 80,
        evidence_note: "Fallback source transparency record."
      }
    ]
  };
}

function reality(
  entity_type: "company" | "industry" | "country",
  entity_id: string,
  entity_name: string,
  score: number,
  label: string,
  roi: number,
  revenue_growth: number,
  margin: number,
  adoption: number
) {
  return {
    entity_type,
    entity_id,
    entity_name,
    score,
    label,
    classification: label,
    components: { roi, revenue_growth, margin, adoption },
    confidence: defaultConfidence,
    confidence_score: defaultConfidence.score,
    source_count: defaultConfidence.source_count,
    last_updated: defaultConfidence.last_updated,
    methodology_note:
      "AI Reality Index is calculated from approved ROI, revenue growth, margin, and adoption metrics."
  };
}
