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
  coverage_score?: number;
  coverage_label?: string;
  coverage?: {
    score: number;
    label: string;
    source_count: number;
    tier_counts: Record<string, number>;
    methodology_note: string;
  };
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
  source_tier?: number;
  credibility_score?: number;
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
