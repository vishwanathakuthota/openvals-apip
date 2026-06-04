export type Confidence = {
  score: number;
  label: string;
  source_count: number;
  last_updated?: string | null;
  source_reliability?: number;
  data_freshness?: number;
  cross_verification?: number;
  methodology_transparency?: number;
};

export type MetricValue = {
  id: string;
  metric_key: string;
  entity_type: EntityType;
  entity_id: string | null;
  value: number;
  unit: string;
  currency?: string | null;
  period_start: string;
  period_end: string;
  methodology?: string;
  confidence: Confidence | null;
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
  score: number;
  label: string;
};

export type CollectionResponse<T = Entity> = {
  items: T[];
  next_cursor: string | null;
};
