# AI Economics Engine

Sprint 7 expands APIP from trust scoring into AI economics intelligence.

## Engine Responsibilities

The AI Economics Engine produces:

- AI Revenue Estimate
- AI Investment Estimate
- AI R&D Spend
- Infrastructure Spend
- AI Profitability Score
- Company intelligence reports

## Public APIs

- `GET /api/v1/ai-revenue`
- `GET /api/v1/ai-investment`
- `GET /api/v1/ai-profitability`
- `GET /api/v1/ai-economics`
- `GET /api/v1/ai-economics/reports/{company_slug}`

All routes require `X-API-Key`.

## Trust Metadata

Every economics record includes:

- Confidence score
- Confidence label
- Trust score
- Trust label
- Source count
- Last updated
- Methodology note
- Source transparency records

## Frontend

The frontend adds:

- `/ai-economics`
- `/ai-profitability`

Both pages display source count, confidence score, and last updated metadata on primary widgets and leaderboard rows.

## V1 Scope

The engine covers:

- Microsoft
- NVIDIA
- Alphabet
- Meta
- Amazon
- OpenAI
- Anthropic
- xAI
- Mistral
- Perplexity

## Publication Guardrail

The economics engine does not claim audited AI segment revenue where companies do not separately disclose it. Outputs are estimates with evidence, confidence, trust, and methodology context.
