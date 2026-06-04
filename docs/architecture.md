# APIP Platform Architecture

Status: Phase 1 architecture draft  
Scope: Documentation only  
Product: APIP, the AI Profitability Intelligence Platform

## Mission

APIP measures whether artificial intelligence investments are producing real economic value. Version 1 is designed to publish transparent AI profitability intelligence across companies, industries, countries, and model families while exposing confidence scores, sources, methodology, public APIs, and an admin workflow for validating metrics.

## Architecture Goals

- Production-grade FastAPI backend and Next.js frontend.
- PostgreSQL as the authoritative system of record.
- Redis for cache, rate limiting, and background job coordination.
- Evidence-first metric governance with source metadata and audit logs.
- Public dashboards and API-key protected public APIs.
- Admin portal for source approval, metric editing, CSV import, ETL execution, and user management.
- Docker Compose for local and small-environment runtime.
- Cloudflare-compatible deployment for `apip.openvalidations.com`.
- GitHub Actions for CI, image builds, and deployment automation.

## System Context

```text
Public users / analysts / admins
  |
  v
Cloudflare DNS, TLS, WAF, CDN, rate limits
  |
  +--> Next.js web app
  |      - public dashboards
  |      - ROI calculator
  |      - admin portal
  |
  +--> FastAPI backend
         - REST API
         - API key enforcement
         - confidence scoring
         - AI Reality Index calculations
         - admin workflows
         - ETL orchestration
         |
         +--> PostgreSQL
         +--> Redis
         +--> Celery workers
         +--> source ingestion pipelines
         +--> object storage for imports/exports
```

## Runtime Services

### Web Service

Next.js, React, TypeScript, Tailwind, and shadcn/ui.

Responsibilities:

- Global AI scoreboard.
- Company, industry, country, and model dashboards.
- AI Reality Index views.
- AI Agent ROI calculator.
- Metric confidence tooltips and source drilldowns.
- Admin portal for authenticated analysts and administrators.

The visual direction from the PRD is a dark, responsive, professional financial terminal aesthetic.

### API Service

FastAPI service responsible for all authoritative reads, writes, calculations, and policy enforcement.

Responsibilities:

- REST API under `/api/v1`.
- Swagger/OpenAPI generation.
- API key authentication for public API access.
- Admin authentication and role-based authorization.
- Company, industry, country, model, metric, source, and confidence endpoints.
- ROI calculator endpoint.
- Calculation services for ROI, profit, AI Reality Index, and confidence scores.
- Audit logging.

### Worker Service

Celery workers connected to Redis.

Responsibilities:

- ETL jobs for filings, reports, CSV imports, and source refreshes.
- Confidence recalculation.
- AI Reality Index recalculation.
- Synthetic seed-data generation for development and demos.
- Report/export generation in later phases.

### PostgreSQL

Source of truth for:

- Users and roles.
- API keys.
- Companies, industries, countries, and AI models.
- Metric values and time series.
- Source metadata and approval state.
- Confidence score inputs and outputs.
- ROI calculator submissions where persisted.
- ETL job records.
- Audit logs.

### Redis

Used for:

- Celery broker/result backend in V1.
- API rate limits by API key, user, and IP.
- Short-lived dashboard aggregate cache.
- Locks for ETL job idempotency.

Redis is not a source of truth.

## Domain Modules

```text
identity
  Users, roles, sessions, API keys.

catalog
  Companies, industries, countries, AI model families, providers.

metrics
  Spend, revenue, profit, ROI, funding, startups, inference cost,
  margin estimates, adoption, growth, and derived values.

sources
  SEC filings, annual reports, earnings calls, investor presentations,
  analyst reports, industry reports, news, and community estimates.

confidence
  Source reliability, freshness, cross verification, methodology transparency,
  confidence labels, and tooltip-ready metadata.

indexes
  AI Reality Index and profitability classifications.

calculator
  AI Agent ROI calculator inputs and outputs.

etl
  CSV import, source ingestion, job execution, and recalculation tasks.

admin
  Source approval, metric editing, user management, and audit review.
```

## Data Flow

### Metric Ingestion

1. Analyst uploads CSV or registers a source in the admin portal.
2. API stores the source in PostgreSQL with status `pending`.
3. Worker validates shape, normalizes values, and creates draft metric records.
4. Analyst or administrator approves the source and associated metrics.
5. API recalculates confidence scores and derived metrics.
6. Public dashboards and APIs expose approved values only.

### Public Dashboard Read

1. User requests dashboard through Cloudflare.
2. Next.js serves cached static assets and requests data from FastAPI.
3. FastAPI checks public access policy and rate limits.
4. FastAPI reads approved metrics from PostgreSQL or aggregate cache from Redis.
5. Response includes value, confidence score, confidence label, source count, and last updated.

### ETL Execution

1. Administrator starts an ETL job.
2. FastAPI creates a durable `etl_jobs` record.
3. FastAPI enqueues a Celery task in Redis.
4. Worker executes the pipeline and writes job events, imported sources, metrics, and errors.
5. FastAPI exposes job status to the admin portal.

## Calculation Engines

### Global Profitability

Global ROI:

```text
global_ai_revenue / global_ai_spend
```

Global net profit:

```text
global_ai_revenue - global_ai_spend
```

Global profitability gauge:

- `YES` when ROI and net profit are materially positive with sufficient confidence.
- `PARTIALLY` when results are mixed or confidence is medium.
- `NO` when spend exceeds revenue with sufficient confidence.

### AI Reality Index

The PRD formula is:

```text
(ROI * 0.4) + (Revenue Growth * 0.3) + (Margin * 0.2) + (Adoption * 0.1)
```

Classifications:

| Score | Label |
| --- | --- |
| 90-100 | Elite |
| 70-89 | Strong |
| 50-69 | Emerging |
| 30-49 | Speculative |
| 0-29 | Cash Burn Zone |

### Confidence Score

The PRD formula is:

```text
(Source Reliability * 0.40)
+ (Data Freshness * 0.20)
+ (Cross Verification * 0.25)
+ (Methodology Transparency * 0.15)
```

Labels:

| Score | Label |
| --- | --- |
| 90-100 | Verified |
| 75-89 | High Confidence |
| 60-74 | Medium Confidence |
| 40-59 | Low Confidence |
| 0-39 | Speculative |

Every public metric response must include the value, confidence score, confidence label, number of sources, and last updated timestamp.

## Security Architecture

- Cloudflare Full (Strict) TLS and WAF in production.
- API key authentication for public API consumers.
- Session or JWT authentication for analysts and administrators.
- Role-based access control: `public`, `analyst`, `admin`.
- Redis-backed rate limiting for public APIs and admin actions.
- Admin-only access to source approval, metric editing, ETL execution, CSV import, audit logs, and user management.
- Secrets stored in deployment platform secret manager and GitHub Actions secrets.
- Audit logs for all source, metric, ETL, API key, and user-management mutations.

## Observability

V1 should include:

- JSON logs with request ID, user ID, API key ID, route, latency, and status code.
- Health endpoints for liveness and readiness.
- Metrics for API latency, error rate, ETL job duration, queue depth, and cache hit rate.
- Error reporting integration such as Sentry.
- Audit views for administrators.

## Scaling Strategy

Initial production:

- One or more Next.js web replicas.
- One or more FastAPI replicas.
- One or more Celery worker replicas.
- Managed PostgreSQL.
- Managed Redis.
- Object storage for CSV uploads and generated exports.

Scale paths:

- Add API replicas for public API traffic.
- Add worker replicas for ETL throughput.
- Cache aggregate dashboard responses in Redis.
- Add PostgreSQL read replicas for analytics-heavy reads.
- Introduce materialized views for time-series dashboard aggregates.

## Key Phase 1 Decisions

| Area | Decision |
| --- | --- |
| Backend | FastAPI |
| Frontend | Next.js, React, TypeScript, Tailwind, shadcn/ui |
| Database | PostgreSQL |
| Cache and broker | Redis |
| Worker | Celery |
| Public edge | Cloudflare |
| CI/CD | GitHub Actions |
| Local runtime | Docker Compose |
| API style | REST with OpenAPI/Swagger |
| Access model | Public read APIs with API keys, authenticated admin portal |
