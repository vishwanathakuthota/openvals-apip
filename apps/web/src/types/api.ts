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
  evidence_classification?: string;
  validation_status?: string;
  openvals_score?: number | null;
  openvals_classification?: string;
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
  source_lineage?: SourceLineage[];
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
  lineage?: SourceLineage | null;
};

export type SourceLineage = {
  source_url: string;
  source_type: string;
  collection_date: string;
  confidence: number;
  evidence_coverage: number;
  reviewer?: string | null;
  approval_date?: string | null;
  validation_status: string;
  evidence_classification: string;
  openvals_score: number;
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

export type MicrosoftValidationSource = {
  id: string;
  title: string;
  source_type: string;
  source_tier: number;
  credibility_score: number;
  publisher?: string | null;
  url?: string | null;
  published_at?: string | null;
  reliability_score: number;
  status: string;
};

export type MicrosoftValidationEvidence = {
  id: string;
  evidence_role: string;
  approval_status: string;
  reviewer_notes?: string | null;
  methodology_trace: string;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  source: MicrosoftValidationSource;
};

export type MicrosoftValidationSection = {
  id: string;
  section_key: string;
  title: string;
  description: string;
  required_source_types: string[];
  coverage_score: number;
  openvals_validation_score: number;
  reviewer_notes?: string | null;
  source_approval_status: string;
  methodology_trace: string;
  lineage: Record<string, string | number | null>[];
  evidence: MicrosoftValidationEvidence[];
};

export type MicrosoftValidationReport = {
  id: string;
  company: string;
  company_slug: string;
  status: string;
  report_path: string;
  methodology_version: string;
  methodology_trace: string;
  reviewer_notes?: string | null;
  evidence_coverage_score: number;
  openvals_validation_score: number;
  openvals_validation_label: string;
  exported_at?: string | null;
  last_updated?: string | null;
  sections: MicrosoftValidationSection[];
  source_lineage: Record<string, string | number | null>[];
};

export type AutonomousEvidenceRecord = {
  id: string;
  company: string;
  company_id: string;
  metric: string;
  metric_name: string;
  previous_value: number | null;
  discovered_value: number;
  source_url: string;
  source_type: string;
  source_title: string;
  evidence_text: string;
  collection_timestamp: string;
  collection_method: string;
  status: string;
  evidence_classification: string;
  confidence_score: number;
  confidence_label: string;
  evidence_coverage_score: number;
  validation_score: number;
  openvals_score: number;
  openvals_classification: string;
  transparency_score: number;
  reproducibility_score: number;
  source_quality_score: number;
  validation_timestamp?: string | null;
  validation_notes?: string | null;
  validation_status: string;
  approval_recommendation?: string | null;
  reviewer?: string | null;
  reviewed_at?: string | null;
  reviewer_decision?: string | null;
  reviewer_notes?: string | null;
  approved_at?: string | null;
  published_at?: string | null;
  version_number: number;
  lineage: SourceLineage;
};

export type TrustCenter = {
  workflow: string;
  auto_publish_enabled: boolean;
  metrics: {
    total_records: number;
    published_records: number;
    approved_records: number;
    under_review_records: number;
    manual_review_required: number;
    average_confidence: number;
    average_openvals_score: number;
    public_lineage_records: number;
  };
  items: AutonomousEvidenceRecord[];
};

export type CompanyOpenValsScore = {
  company: string;
  company_slug: string;
  openvals_score: number;
  classification: string;
  published_records: number;
  evidence_coverage_score: number;
  confidence_score: number;
  source_count: number;
  last_updated?: string | null;
  methodology_note: string;
};
