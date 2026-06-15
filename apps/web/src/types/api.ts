export type Confidence = {
  score: number;
  label: string;
  source_count: number;
  last_updated?: string | null;
  source_reliability?: number;
  data_freshness?: number;
  cross_verification?: number;
  methodology_transparency?: number;
  methodology_note?: string;
};

export type MetricValue = {
  id: string;
  metric_key: string;
  entity_type: EntityType;
  entity_id: string | null;
  value: number;
  confidence_score?: number | null;
  confidence_label?: string | null;
  source_count?: number;
  last_updated?: string | null;
  methodology_note?: string;
  unit: string;
  currency?: string | null;
  period_start: string;
  period_end: string;
  methodology?: string;
  confidence: Confidence | null;
  sources?: SourceTransparency[];
};

export type SourceTransparency = {
  id: string;
  title: string;
  source_type: string;
  publisher?: string | null;
  url?: string | null;
  published_at?: string | null;
  reliability_score: number;
  evidence_note?: string | null;
};

export type EntityType = "company" | "industry" | "country" | "model" | "global";

export type Entity = {
  id: string;
  name: string;
  slug?: string;
  ticker?: string | null;
  iso_code?: string;
  region?: string | null;
  website_url?: string | null;
  model_family?: string;
  status?: string;
  metrics?: MetricValue[];
};

export type Scoreboard = {
  total_ai_spend: number;
  total_ai_revenue: number;
  net_profit: number;
  global_roi: number;
  profitability_gauge: "YES" | "NO" | "PARTIALLY";
  companies_tracked: number;
  industries_tracked: number;
  countries_tracked: number;
  confidence: Confidence;
  top_ai_reality_index: RealityIndexItem[];
};

export type RealityIndexItem = {
  entity_type: EntityType;
  entity_id: string;
  entity_name?: string;
  score: number;
  label: string;
  classification?: string;
  components?: {
    roi: number;
    revenue_growth: number;
    margin: number;
    adoption: number;
  };
  confidence?: Confidence;
  confidence_score?: number;
  source_count?: number;
  last_updated?: string | null;
  methodology_note?: string;
};

export type CollectionResponse<T = Entity> = {
  items: T[];
  next_cursor: string | null;
};

export type EconomicsSource = {
  id: string;
  title: string;
  source_type: string;
  publisher?: string | null;
  url?: string | null;
  published_at?: string | null;
  reliability_score: number;
};

export type AiEconomicsBase = {
  company: string;
  company_slug: string;
  ticker?: string | null;
  confidence: Confidence;
  confidence_score: number;
  confidence_label: string;
  trust_score: number;
  trust_label: string;
  source_count: number;
  sources: EconomicsSource[];
  last_updated: string;
  methodology_note: string;
};

export type AiRevenueEstimate = AiEconomicsBase & {
  input_revenue: number;
  ai_revenue_estimate: number;
  ai_revenue_share: number;
  inputs: string[];
};

export type AiInvestmentEstimate = AiEconomicsBase & {
  ai_investment: number;
  ai_rd_spend: number;
  infrastructure_spend: number;
  investment_intensity: number;
};

export type AiProfitabilityScore = AiEconomicsBase & {
  score: number;
  rating: string;
  classification: string;
  components: {
    revenue_efficiency: number;
    ai_revenue_growth: number;
    ai_margin_proxy: number;
    infrastructure_roi: number;
    capital_efficiency: number;
  };
  formula: string;
};

export type AiEconomicsReport = AiEconomicsBase & {
  ai_revenue_estimate: number;
  ai_investment: number;
  ai_rd_spend: number;
  infrastructure_spend: number;
  ai_profitability_score: number;
  classification: string;
  executive_summary: string;
  evidence_sections: string[];
};

export type AiEconomicsDashboard = {
  summary: {
    companies_tracked: number;
    estimated_ai_revenue: number;
    estimated_ai_investment: number;
    estimated_ai_profit: number;
    average_profitability_score: number;
    average_confidence_score: number;
    source_count: number;
    last_updated: string;
    methodology_note: string;
  };
  ai_revenue: AiRevenueEstimate[];
  ai_investment: AiInvestmentEstimate[];
  ai_profitability: AiProfitabilityScore[];
  intelligence_reports: AiEconomicsReport[];
};
