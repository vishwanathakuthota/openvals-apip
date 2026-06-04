# APIP Database Schema

Status: Phase 1 logical schema draft  
Database: PostgreSQL

## Design Principles

- Store approved public metrics separately from draft imports.
- Preserve source lineage for every published metric.
- Make confidence scoring reproducible from stored inputs.
- Support company, industry, country, and model dashboards from the same metric model.
- Use audit logs for every admin mutation.
- Use UUID primary keys and timestamp columns for all major entities.

## Extensions

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
```

## Core Entity Map

```text
users 1---n audit_logs
users 1---n api_keys

companies 1---n metric_values
industries 1---n metric_values
countries 1---n metric_values
ai_models 1---n metric_values

metric_definitions 1---n metric_values
metric_values n---n sources through metric_sources
metric_values 1---1 confidence_scores

etl_jobs 1---n etl_job_events
```

## Identity and Access

### users

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| email | citext | Unique |
| full_name | text | Required |
| role | text | `analyst`, `admin` |
| status | text | `active`, `invited`, `disabled` |
| password_hash | text | Nullable if external auth is used |
| last_login_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique index on `email`.
- Index on `(role, status)`.

### api_keys

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| name | text | Display name |
| key_hash | text | Hashed API key |
| prefix | text | Non-secret visible prefix |
| owner_user_id | uuid | FK to `users.id`, nullable for system keys |
| scopes | text[] | Example: `public:read`, `metrics:read` |
| rate_limit_per_minute | integer | Required |
| status | text | `active`, `revoked` |
| last_used_at | timestamptz | Nullable |
| expires_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique index on `key_hash`.
- Index on `(status, expires_at)`.

## Catalog Tables

### companies

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| name | text | Required |
| slug | citext | Unique |
| ticker | text | Nullable |
| headquarters_country_id | uuid | FK to `countries.id`, nullable |
| website_url | text | Nullable |
| status | text | `active`, `archived` |
| metadata | jsonb | Additional profile data |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### industries

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| name | text | Required |
| slug | citext | Unique |
| parent_industry_id | uuid | Self FK, nullable |
| status | text | `active`, `archived` |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### countries

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| name | text | Required |
| iso_code | char(2) | Unique |
| region | text | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### ai_models

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| name | text | Required |
| slug | citext | Unique |
| provider_company_id | uuid | FK to `companies.id`, nullable |
| model_family | text | Example: GPT, Claude, Gemini, Grok |
| status | text | `active`, `archived` |
| metadata | jsonb | Context window, modalities, release data |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

## Metrics

### metric_definitions

Defines available metric types.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| key | citext | Unique, example: `ai_spend` |
| name | text | Human label |
| description | text | Required |
| unit | text | `usd`, `percent`, `count`, `ratio`, `score` |
| higher_is_better | boolean | Required |
| aggregation_method | text | `sum`, `average`, `latest`, `weighted_average` |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Required V1 metric keys:

- `ai_spend`
- `ai_revenue`
- `net_profit`
- `roi`
- `funding`
- `startup_count`
- `inference_cost`
- `gross_margin`
- `net_margin`
- `revenue_growth`
- `adoption`
- `ai_reality_index`

### metric_values

Stores values for companies, industries, countries, models, and global aggregates.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| metric_definition_id | uuid | FK to `metric_definitions.id` |
| entity_type | text | `global`, `company`, `industry`, `country`, `model` |
| entity_id | uuid | Nullable for `global` |
| period_start | date | Required |
| period_end | date | Required |
| value_numeric | numeric(20,6) | Required |
| currency | char(3) | Nullable, default USD for money |
| methodology | text | Calculation or estimate method |
| status | text | `draft`, `approved`, `rejected`, `superseded` |
| created_by_user_id | uuid | FK to `users.id`, nullable |
| approved_by_user_id | uuid | FK to `users.id`, nullable |
| approved_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Index on `(entity_type, entity_id, period_end DESC)`.
- Index on `(metric_definition_id, status, period_end DESC)`.
- Unique partial index for one approved value per metric/entity/period.

## Sources and Confidence

### sources

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| title | text | Required |
| source_type | text | `sec_filing`, `annual_report`, `earnings_call`, `investor_presentation`, `analyst_estimate`, `industry_report`, `news_article`, `community_estimate` |
| url | text | Nullable |
| publisher | text | Nullable |
| published_at | timestamptz | Nullable |
| reliability_score | integer | 0 to 100 |
| status | text | `pending`, `approved`, `rejected`, `archived` |
| uploaded_by_user_id | uuid | FK to `users.id`, nullable |
| approved_by_user_id | uuid | FK to `users.id`, nullable |
| approved_at | timestamptz | Nullable |
| metadata | jsonb | Filing IDs, page refs, extraction details |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### metric_sources

Join table linking metrics to sources.

| Column | Type | Notes |
| --- | --- | --- |
| metric_value_id | uuid | FK to `metric_values.id` |
| source_id | uuid | FK to `sources.id` |
| evidence_note | text | Optional |
| created_at | timestamptz | Required |

Primary key:

- `(metric_value_id, source_id)`

### confidence_scores

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| metric_value_id | uuid | Unique FK to `metric_values.id` |
| source_reliability | integer | 0 to 100 |
| data_freshness | integer | 0 to 100 |
| cross_verification | integer | 0 to 100 |
| methodology_transparency | integer | 0 to 100 |
| confidence_score | numeric(5,2) | Final weighted score |
| confidence_label | text | `verified`, `high`, `medium`, `low`, `speculative` |
| source_count | integer | Required |
| calculated_at | timestamptz | Required |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

## ROI Calculator

### roi_calculations

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| user_id | uuid | FK to `users.id`, nullable for anonymous/public |
| provider | text | Required |
| users_count | integer | Required |
| tokens_per_user | integer | Required |
| infrastructure_cost | numeric(14,2) | Required |
| employees_count | integer | Required |
| subscription_price | numeric(14,2) | Required |
| revenue | numeric(14,2) | Calculated |
| cost | numeric(14,2) | Calculated |
| gross_margin | numeric(10,4) | Calculated |
| net_margin | numeric(10,4) | Calculated |
| break_even_users | integer | Calculated |
| created_at | timestamptz | Required |

## ETL and Admin

### etl_jobs

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| job_type | text | `csv_import`, `source_refresh`, `recalculate_metrics`, `seed_data` |
| status | text | `queued`, `running`, `succeeded`, `failed`, `cancelled` |
| requested_by_user_id | uuid | FK to `users.id` |
| input_uri | text | Optional object storage path |
| parameters | jsonb | Job options |
| error_message | text | Nullable |
| started_at | timestamptz | Nullable |
| completed_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### etl_job_events

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| etl_job_id | uuid | FK to `etl_jobs.id` |
| level | text | `info`, `warning`, `error` |
| message | text | Required |
| metadata | jsonb | Optional |
| created_at | timestamptz | Required |

### audit_logs

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| actor_user_id | uuid | FK to `users.id`, nullable |
| action | text | Machine-readable action |
| target_type | text | Example: `source`, `metric_value`, `etl_job`, `user` |
| target_id | uuid | Nullable |
| request_id | text | Trace correlation |
| ip_address | inet | Nullable |
| user_agent | text | Nullable |
| metadata | jsonb | Event details |
| created_at | timestamptz | Required |

## Seed Data Requirement

The PRD requires synthetic but realistic data for:

- 50 companies.
- 10 industries.
- 10 countries.
- Years 2021 through 2026.

Seed data should be generated through an explicit seed command or ETL job, not through schema migrations.

## Migration Strategy

- Use Alembic.
- Prefer additive, backward-compatible migrations.
- Keep enum-like fields as check constraints or lookup tables until values stabilize.
- Use materialized views later for dashboard aggregates if query load requires them.
