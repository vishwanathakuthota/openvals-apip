# AI Economy Coverage Expansion

Sprint: 3

Branch: `feature/ai-economy-expansion`

## Goal

Expand APIP from three Gold Standard companies to ten validated AI economy companies.

## Validated Company Set

| Rank | Company | Route Slug | Validation Tier |
| ---: | --- | --- | --- |
| 1 | Microsoft | `microsoft` | Gold Standard |
| 2 | NVIDIA | `nvidia` | Gold Standard |
| 3 | Alphabet | `alphabet` | Gold Standard |
| 4 | Meta | `meta` | AI Economy Validated |
| 5 | Amazon | `amazon` | AI Economy Validated |
| 6 | OpenAI | `openai` | AI Economy Validated |
| 7 | Anthropic | `anthropic` | AI Economy Validated |
| 8 | xAI | `xai` | AI Economy Validated |
| 9 | Mistral | `mistral` | AI Economy Validated |
| 10 | Perplexity | `perplexity` | AI Economy Validated |

## Workflow

All ten companies use the APIP trust workflow:

`COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH`

The Research Agent collects evidence from approved source registry entries. The Validation Agent calculates Confidence Score, Evidence Coverage Score, Validation Score, and OpenVals Score. The Approval Agent recommends actions, and the Publisher Agent publishes only approved records.

## Public Artifact Routes

Each company exposes:

- `/companies/{slug}/validation-report`
- `/companies/{slug}/evidence-timeline`
- `/companies/{slug}/source-lineage`
- `/companies/{slug}/openvals-score`
- `/companies/{slug}/trust-report`

For Alphabet, public routes use `alphabet`; backend data continues to map to the existing `google` company slug.

## API Coverage

Each validated company is included in:

- `GET /api/v1/leaderboard`
- `GET /api/v1/trust-index`
- `GET /api/v1/trust-center`
- `GET /api/v1/companies`
- `GET /api/v1/metrics/search`

Each company publishes six core AI economy metrics:

- `ai_revenue`
- `ai_spend`
- `roi`
- `revenue_growth`
- `gross_margin`
- `adoption`

## Evidence Model

Public companies use higher-trust evidence expectations:

- SEC filing
- Annual report
- Earnings call
- Investor presentation

Private AI companies use approved public company statements for beta validation because audited AI economics filings are not available. APIP marks the limitation through source type, confidence, coverage, methodology notes, and lineage.

## Trust Outputs

For every validated company, APIP generates:

- Trust profile
- Source lineage
- Evidence timeline
- OpenVals Score
- Confidence Score
- Evidence Coverage Score
- Trust Report
- Validation Report

## Test Coverage

Automated API tests verify:

- All ten companies appear in the Trust Index leaderboard.
- All ten companies have published records.
- All ten companies expose validation report, evidence timeline, source lineage, OpenVals score, and trust report endpoints.
- Metric payloads retain confidence, coverage, OpenVals Score, source lineage, and validation status.

## Launch Positioning

Microsoft, NVIDIA, and Alphabet remain Gold Standard companies. Meta, Amazon, OpenAI, Anthropic, xAI, Mistral, and Perplexity are AI Economy Validated companies for beta coverage expansion.
