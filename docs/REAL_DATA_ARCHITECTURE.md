# APIP Real Data Architecture

Status: Beta implementation  
Scope: Phase 1 company data for Microsoft, Google, Meta, Amazon, NVIDIA, OpenAI, Anthropic, xAI, Mistral, and Perplexity.

## Objective

APIP beta replaces synthetic source placeholders with a source-backed registry and metric evidence model. Direct AI economics disclosure varies by company, so APIP stores beta proxy metrics with explicit source lineage, confidence scores, evidence coverage, and methodology notes.

## Source Priority Model

APIP assigns each source type to a tier:

| Tier | Source types | Use |
| --- | --- | --- |
| Tier 1 | SEC filings, annual reports, earnings calls | Primary evidence for public-company financial metrics |
| Tier 2 | Investor presentations, public company statements | Company-issued support where direct filing segmentation is incomplete |
| Tier 3 | Stanford AI Index, OECD AI Observatory, IMF, World Bank | Institutional context and macro validation |
| Tier 4 | Reuters, Bloomberg, Financial Times | Trusted journalism for corroboration only |

The source registry stores approved source records in the existing `sources` table. Each source has title, URL, publisher, source type, reliability score, published date, and status.

## Phase 1 Source Registry

The beta registry includes:

- Microsoft: SEC EDGAR registry and Microsoft 2025 Annual Report
- Google: Alphabet SEC EDGAR registry and Alphabet investor relations
- Meta: SEC EDGAR registry and Meta investor relations
- Amazon: SEC EDGAR registry and Amazon investor relations
- NVIDIA: SEC EDGAR registry and NVIDIA FY2025 Annual Report
- OpenAI, Anthropic, xAI, Mistral, Perplexity: public company statements
- Stanford AI Index, OECD AI Observatory, IMF AI hub, and World Bank digital development hub as shared Tier 3 context

Code entry points:

- `services/api/app/domains/sources/registry.py`
- `services/api/app/domains/sources/credibility.py`
- `services/api/app/db/seed.py`

## Source Credibility Engine

The credibility engine combines:

- Source reliability from the Confidence Score Engine taxonomy
- Freshness score
- Tier adjustment

Output:

- `source_tier`
- `credibility_score`
- existing `reliability_score`

Public source payloads and metric source transparency payloads expose these fields.

## Evidence Coverage Score

Coverage answers a different question from confidence:

- Confidence: how reliable the metric estimate is.
- Coverage: how complete the supporting evidence stack is.

Coverage weights:

- Tier 1: 45 points
- Tier 2: 25 points
- Tier 3: 20 points
- Tier 4: 10 points
- Additional sources in the same tier add up to 5 points each, capped by tier.

Coverage labels:

- `90-100`: Full Coverage
- `70-89`: Strong Coverage
- `50-69`: Partial Coverage
- `30-49`: Thin Coverage
- `0-29`: Unverified Coverage

Every metric response includes:

- `sources`
- `confidence_score`
- `confidence_label`
- `coverage_score`
- `coverage_label`
- `last_updated`

## Source Lineage Tracking

Metric lineage is tracked through `metric_sources`, which links approved metric values to approved sources. Catalog import lineage is tracked through `data_lineage`, which records source URL, source type, confidence score, imported by, imported date, import batch, and metadata snapshot.

Admin review history is tracked through:

- `source_metrics`
- `metric_versions`
- `audit_logs`

## Ingestion Connectors

Beta provides connector foundations for:

- SEC filings: `SecFilingsConnector` builds official EDGAR source records from CIK values.
- CSV imports: `CsvImportConnector` reuses the validated financial metrics CSV row parser.
- Manual research entries: `ManualResearchConnector` creates pending source metrics from analyst-entered evidence.

Admin endpoints:

- `POST /api/v1/admin/imports/csv`
- `POST /api/v1/admin/imports/catalog/{entity_type}/csv`
- `POST /api/v1/admin/research-entries`
- `GET /api/v1/admin/source-metrics`
- `PATCH /api/v1/admin/source-metrics/{id}/approve`
- `PATCH /api/v1/admin/source-metrics/{id}/reject`

## Beta Methodology Guardrails

APIP beta does not claim private-company AI economics are audited financial statements. Where direct AI segment disclosure is unavailable, the metric methodology note marks the value as a source-backed proxy. Coverage and confidence scores make that limitation visible in the API and UI.
