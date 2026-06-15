import type { AiEconomicsDashboard, CollectionResponse, Entity, MetricValue, Scoreboard } from "@/types/api";

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
      { id: "company_nvidia", name: "NVIDIA", slug: "nvidia", ticker: "NVDA", status: "active" },
      { id: "company_alphabet", name: "Alphabet", slug: "alphabet", ticker: "GOOGL", status: "active" },
      { id: "company_xai", name: "xAI", slug: "xai", ticker: null, status: "active" },
      { id: "company_mistral", name: "Mistral", slug: "mistral", ticker: null, status: "active" },
      { id: "company_perplexity", name: "Perplexity", slug: "perplexity", ticker: null, status: "active" }
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

const economicsSources = [
  {
    id: "src_annual_report_registry",
    title: "APIP Annual Report Evidence Registry",
    source_type: "annual_report",
    publisher: "OpenVals",
    url: "https://apip.openvalidations.com/methodology#annual-reports",
    published_at: "2026-05-20T00:00:00Z",
    reliability_score: 95
  },
  {
    id: "src_investor_presentation_registry",
    title: "APIP Investor Presentation Evidence Registry",
    source_type: "investor_presentation",
    publisher: "OpenVals",
    url: "https://apip.openvalidations.com/methodology#investor-presentations",
    published_at: "2026-04-15T00:00:00Z",
    reliability_score: 80
  },
  {
    id: "src_industry_research_registry",
    title: "APIP Industry and Research Evidence Registry",
    source_type: "industry_report",
    publisher: "OpenVals",
    url: "https://apip.openvalidations.com/methodology#industry-research",
    published_at: "2026-02-15T00:00:00Z",
    reliability_score: 65
  }
];

const economicsCompanies = [
  ["NVIDIA", "nvidia", "NVDA", 91000000000, 31000000000, 86.8, "Elite AI Economics"],
  ["Microsoft", "microsoft", "MSFT", 42000000000, 38000000000, 66.3, "Efficient AI Builder"],
  ["Alphabet", "alphabet", "GOOGL", 39000000000, 49000000000, 55.7, "Investment Heavy"],
  ["OpenAI", "openai", null, 12500000000, 16000000000, 54.5, "Investment Heavy"],
  ["Meta", "meta", "META", 24000000000, 33000000000, 50.8, "Investment Heavy"],
  ["Amazon", "amazon", "AMZN", 47000000000, 57000000000, 49.1, "Early Economics"],
  ["Anthropic", "anthropic", null, 3900000000, 7800000000, 38.7, "Early Economics"],
  ["Perplexity", "perplexity", null, 390000000, 820000000, 34.1, "Early Economics"],
  ["Mistral", "mistral", null, 430000000, 1100000000, 31.2, "Early Economics"],
  ["xAI", "xai", null, 1300000000, 5700000000, 29.8, "Early Economics"]
] as const;

export const fallbackAiEconomics: AiEconomicsDashboard = {
  summary: {
    companies_tracked: economicsCompanies.length,
    estimated_ai_revenue: economicsCompanies.reduce((sum, company) => sum + company[3], 0),
    estimated_ai_investment: economicsCompanies.reduce((sum, company) => sum + company[4], 0),
    estimated_ai_profit:
      economicsCompanies.reduce((sum, company) => sum + company[3], 0) -
      economicsCompanies.reduce((sum, company) => sum + company[4], 0),
    average_profitability_score:
      economicsCompanies.reduce((sum, company) => sum + company[5], 0) / economicsCompanies.length,
    average_confidence_score: 78.4,
    source_count: 30,
    last_updated: defaultConfidence.last_updated,
    methodology_note:
      "AI economics estimates combine approved APIP metric records, source reliability, freshness, and disclosure profiles."
  },
  ai_revenue: economicsCompanies.map(([company, company_slug, ticker, revenue]) => ({
    ...economicsBase(company, company_slug, ticker),
    input_revenue: revenue * 4,
    ai_revenue_estimate: revenue,
    ai_revenue_share: 0.18,
    inputs: ["Revenue", "Earnings Calls", "Investor Presentations", "SEC Filings", "Public AI disclosures"]
  })),
  ai_investment: economicsCompanies.map(([company, company_slug, ticker, , investment]) => ({
    ...economicsBase(company, company_slug, ticker),
    ai_investment: investment,
    ai_rd_spend: investment * 0.35,
    infrastructure_spend: investment * 0.65,
    investment_intensity: 0.16
  })),
  ai_profitability: economicsCompanies.map(([company, company_slug, ticker, revenue, investment, score, classification]) => ({
    ...economicsBase(company, company_slug, ticker),
    score,
    rating: score >= 85 ? "A" : score >= 75 ? "B" : score >= 65 ? "C" : score >= 50 ? "D" : "F",
    classification,
    components: {
      revenue_efficiency: Math.min(100, (revenue / investment) * 55),
      ai_revenue_growth: company === "NVIDIA" ? 51 : 27,
      ai_margin_proxy: company === "NVIDIA" ? 74 : 50,
      infrastructure_roi: Math.min(100, (revenue / (investment * 0.65)) * 45),
      capital_efficiency: Math.min(100, (revenue / (revenue * 4)) * 240)
    },
    formula:
      "25% Revenue Efficiency + 20% AI Revenue Growth + 20% AI Margin Proxy + 20% Infrastructure ROI + 15% Capital Efficiency"
  })),
  intelligence_reports: economicsCompanies.map(([company, company_slug, ticker, revenue, investment, score, classification]) => ({
    ...economicsBase(company, company_slug, ticker),
    ai_revenue_estimate: revenue,
    ai_investment: investment,
    ai_rd_spend: investment * 0.35,
    infrastructure_spend: investment * 0.65,
    ai_profitability_score: score,
    classification,
    executive_summary: `${company} AI economics estimate compares AI revenue evidence against AI investment evidence with confidence and trust metadata.`,
    evidence_sections: ["Revenue", "Earnings Calls", "Investor Presentations", "SEC Filings", "Public AI Disclosures"]
  }))
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

function economicsBase(company: string, company_slug: string, ticker: string | null) {
  return {
    company,
    company_slug,
    ticker,
    confidence: defaultConfidence,
    confidence_score: defaultConfidence.score,
    confidence_label: defaultConfidence.label,
    trust_score: 78,
    trust_label: "Reliable",
    source_count: economicsSources.length,
    sources: economicsSources,
    last_updated: defaultConfidence.last_updated,
    methodology_note:
      "APIP estimate calculated from approved evidence records and normalized company disclosure profiles."
  };
}
