# APIP API Specification

Status: Phase 1 REST contract draft  
Backend: FastAPI  
Base path: `/api/v1`

## API Principles

- JSON over HTTPS.
- OpenAPI/Swagger required.
- Public read endpoints require API keys once API access is externalized.
- Admin endpoints require authenticated analyst/admin users.
- All metric responses include confidence and source metadata.
- Only approved metrics and approved sources are exposed through public endpoints.

## Authentication

Public API:

```http
X-API-Key: apip_live_...
X-Request-ID: <client-request-id>
```

Admin API:

```http
Authorization: Bearer <admin-token>
X-Request-ID: <client-request-id>
```

## Standard Metric Shape

```json
{
  "metric_key": "ai_revenue",
  "value": 1250000000,
  "unit": "usd",
  "period_start": "2026-01-01",
  "period_end": "2026-12-31",
  "confidence": {
    "score": 82.5,
    "label": "High Confidence",
    "source_count": 4,
    "last_updated": "2026-06-04T09:00:00Z"
  },
  "sources": [
    {
      "id": "src_123",
      "title": "FY2026 Investor Presentation",
      "source_type": "investor_presentation",
      "url": "https://example.com/report.pdf"
    }
  ]
}
```

## Standard Error Shape

```json
{
  "error": {
    "code": "validation_failed",
    "message": "One or more fields are invalid.",
    "details": [],
    "request_id": "req_123"
  }
}
```

## Health

### GET /health/live

Returns process liveness.

### GET /health/ready

Returns database, Redis, and worker-readiness status.

### GET /api/v1/health

Returns deployment health for production reverse proxies and smoke tests.

Response:

```json
{
  "status": "ok",
  "checks": {
    "api": "ok",
    "postgres": "ok",
    "redis": "ok"
  }
}
```

## Public Dashboard APIs

### GET /api/v1/scoreboard

Returns the Global AI Scoreboard.

Response:

```json
{
  "total_ai_spend": 420000000000,
  "total_ai_revenue": 310000000000,
  "net_profit": -110000000000,
  "global_roi": 0.7381,
  "profitability_gauge": "PARTIALLY",
  "companies_tracked": 50,
  "industries_tracked": 10,
  "countries_tracked": 10,
  "confidence": {
    "score": 71.4,
    "label": "Medium Confidence",
    "source_count": 184,
    "last_updated": "2026-06-04T09:00:00Z"
  }
}
```

### GET /api/v1/ai-reality-index

Returns ranked AI Reality Index entities calculated from approved ROI, revenue growth, margin, and adoption metrics.

Query parameters:

- `entity_type`: `company`, `industry`, `country`, optional.
- `limit`: default 25, maximum 100.

Formula:

```text
AI Reality Index = (ROI * 0.4) + (Revenue Growth * 0.3) + (Margin * 0.2) + (Adoption * 0.1)
```

Response:

```json
{
  "items": [
    {
      "entity_type": "company",
      "entity_id": "company_nvidia",
      "entity_name": "NVIDIA",
      "score": 88.9,
      "label": "Strong",
      "classification": "Strong",
      "components": {
        "roi": 94,
        "revenue_growth": 88,
        "margin": 74,
        "adoption": 91
      },
      "confidence": {
        "score": 82.5,
        "label": "High Confidence",
        "source_count": 12,
        "last_updated": "2026-06-04T09:00:00Z",
        "methodology_note": "AI Reality Index is calculated from approved component metrics."
      }
    }
  ]
}
```

Classifications:

- `90-100`: Elite
- `70-89`: Strong
- `50-69`: Emerging
- `30-49`: Speculative
- `0-29`: Cash Burn Zone

## Companies

### GET /api/v1/companies

Lists companies.

Query parameters:

- `q`
- `industry`
- `country`
- `limit`
- `cursor`

### GET /api/v1/companies/{company_id}

Returns company profile, latest metrics, sources, confidence labels, and trend summaries.

### GET /api/v1/companies/{company_id}/metrics

Query parameters:

- `metric_key`
- `from_year`
- `to_year`

Returns time-series metrics for the company.

Required company dashboard metrics:

- Spend.
- Revenue.
- Profit.
- ROI.
- Trend charts.
- Sources.
- Confidence scores.

## Industries

### GET /api/v1/industries

Lists industries tracked by APIP.

### GET /api/v1/industries/{industry_id}

Returns industry profile, profitability heatmap data, latest metrics, and confidence.

### GET /api/v1/industries/{industry_id}/metrics

Returns industry metric time series.

## Countries

### GET /api/v1/countries

Lists countries tracked by APIP.

### GET /api/v1/countries/{country_id}

Returns country profile, spend, revenue, ROI, startup count, funding, and confidence.

### GET /api/v1/countries/{country_id}/metrics

Returns country metric time series.

## Models

### GET /api/v1/models

Lists AI models/model families.

### GET /api/v1/models/{model_id}

Returns model economics:

- Inference cost.
- Revenue estimate.
- Margin estimate.
- Growth rate.
- Confidence.
- Sources.

### GET /api/v1/models/{model_id}/metrics

Returns model metric time series.

## Metrics

### GET /api/v1/metrics

Lists metric definitions.

### GET /api/v1/metrics/search

Searches approved metric values.

Query parameters:

- `entity_type`: `global`, `company`, `industry`, `country`, `model`.
- `entity_id`
- `metric_key`
- `period_start`
- `period_end`
- `confidence_min`

## Confidence

### GET /api/v1/confidence/{metric_value_id}

Returns confidence inputs and final score for one metric.

Response:

```json
{
  "metric_value_id": "met_123",
  "source_reliability": 90,
  "data_freshness": 75,
  "cross_verification": 80,
  "methodology_transparency": 70,
  "confidence_score": 80.0,
  "confidence_label": "High Confidence",
  "formula": "(Source Reliability * 0.40) + (Data Freshness * 0.20) + (Cross Verification * 0.25) + (Methodology Transparency * 0.15)"
}
```

## ROI Calculator

### POST /api/v1/roi-calculator

Calculates AI agent economics.

Request:

```json
{
  "users": 2500,
  "tokens_per_user": 120000,
  "provider": "OpenAI",
  "infrastructure_cost": 15000,
  "employees": 8,
  "subscription_price": 49
}
```

Response:

```json
{
  "revenue": 122500,
  "cost": 43800,
  "gross_margin": 0.6424,
  "net_margin": 0.312,
  "break_even_users": 894
}
```

## Sources

### GET /api/v1/sources

Lists approved public sources.

### GET /api/v1/sources/{source_id}

Returns source metadata and linked metrics.

## Admin APIs

Admin routes are under `/api/v1/admin`.

All admin routes require an admin JWT:

```http
Authorization: Bearer <admin-token>
```

### GET /api/v1/admin/api-keys

Lists API keys by prefix, plan, status, and usage. Plaintext keys are never returned after creation.

### POST /api/v1/admin/api-keys

Generates a new API key. The plaintext `api_key` is returned once.

Request:

```json
{
  "name": "Partner Integration",
  "plan": "pro"
}
```

Response:

```json
{
  "id": "key_123",
  "name": "Partner Integration",
  "key_prefix": "apip_live_abcd",
  "api_key": "apip_live_abcd...",
  "plan": "pro",
  "daily_limit": 5000,
  "status": "active"
}
```

### PATCH /api/v1/admin/api-keys/{api_key_id}

Updates API key name, plan, or status.

### GET /api/v1/admin/dashboard

Returns admin counts for catalog entities, sources, pending imported metrics, and audit logs.

### GET /api/v1/admin/companies

Lists companies for administration.

### POST /api/v1/admin/companies

Creates a company.

### PATCH /api/v1/admin/companies/{company_id}

Updates company metadata or status.

### GET /api/v1/admin/industries

Lists industries for administration.

### POST /api/v1/admin/industries

Creates an industry.

### PATCH /api/v1/admin/industries/{industry_id}

Updates industry metadata or status.

### GET /api/v1/admin/countries

Lists countries for administration.

### POST /api/v1/admin/countries

Creates a country.

### PATCH /api/v1/admin/countries/{country_id}

Updates country metadata.

### GET /api/v1/admin/models

Lists AI models for administration.

### POST /api/v1/admin/models

Creates an AI model.

### PATCH /api/v1/admin/models/{model_id}

Updates AI model metadata or status.

### GET /api/v1/admin/sources

Lists all sources, including pending and rejected sources.

### POST /api/v1/admin/sources

Creates a source record.

### PATCH /api/v1/admin/sources/{source_id}

Updates source metadata or status.

### PATCH /api/v1/admin/sources/{source_id}/approve

Approves a source.

### PATCH /api/v1/admin/sources/{source_id}/reject

Rejects a source.

### POST /api/v1/admin/metrics

Creates a draft metric value.

### PATCH /api/v1/admin/metrics/{metric_value_id}

Edits a metric value.

### PATCH /api/v1/admin/metrics/{metric_value_id}/approve

Approves a metric and triggers confidence/derived metric recalculation.

### POST /api/v1/admin/imports/csv

Uploads a financial metrics CSV file, validates each row, creates pending `source_metrics`, calculates preliminary confidence scores, and writes import audit logs.

Multipart form field:

- `file`: `.csv`

Required CSV columns:

- `company`
- `year`
- `metric_type`
- `value`
- `source_url`
- `source_type`

Response:

```json
{
  "imported_count": 1,
  "items": [
    {
      "id": "srcmet_123",
      "company": "OpenAI",
      "year": 2026,
      "metric_type": "ai_revenue",
      "value": 12500000000,
      "source_url": "https://example.com/openai-annual-report",
      "source_type": "annual_report",
      "confidence_score": 75.5,
      "approved_status": "pending"
    }
  ]
}
```

### GET /api/v1/admin/source-metrics

Lists imported metrics for admin review. Optional query parameter:

- `approved_status`: `pending`, `approved`, or `rejected`

### PATCH /api/v1/admin/source-metrics/{source_metric_id}/approve

Approves an imported metric, publishes it to canonical `metric_values`, links the approved source, recalculates confidence, creates a metric version, and writes audit logs.

### PATCH /api/v1/admin/source-metrics/{source_metric_id}/reject

Rejects an imported metric and source without publishing it to public metric responses.

### GET /api/v1/admin/audit-logs

Lists source workflow and metric publication audit logs.

Response:

```json
{
  "items": [
    {
      "id": "audit_123",
      "actor": "APIP Admin",
      "action": "source_metric.approved",
      "target_type": "source_metric",
      "target_id": "srcmet_123",
      "metadata": {
        "source_id": "src_123"
      },
      "created_at": "2026-06-04T09:00:00Z"
    }
  ],
  "next_cursor": null
}
```

### POST /api/v1/admin/seed-import

Runs the idempotent seed import and writes an audit event.

### GET /api/v1/admin/users

Lists admin/analyst users.

### PATCH /api/v1/admin/users/{user_id}

Updates role or status.

## Rate Limits

Daily API key tiers:

- Free: 100 requests per day.
- Pro: 5,000 requests per day.
- Enterprise: unlimited.

The V1 foundation stores daily counters on `api_keys`. Redis-backed distributed limits can be layered on top of the same plan model for multi-instance deployments.

## OpenAPI Exposure

- Expose `/openapi.json`.
- Expose `/docs` and `/redoc` in development and staging.
- Protect or disable interactive Swagger in production admin contexts.
