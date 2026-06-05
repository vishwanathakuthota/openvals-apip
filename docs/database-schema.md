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
sources 1---n source_metrics
sources 1---n data_lineage
source_metrics 1---n metric_versions
metric_values n---n sources through metric_sources
metric_values 1---1 confidence_scores

users 1---n source_metrics
users 1---n data_lineage
companies 1---1 company_validations
company_validations 1---n company_validation_evidence
company_validations 1---n company_validation_source_reviews
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
| key_prefix | text | Non-secret visible prefix |
| key_hash | text | Hashed API key |
| plan | text | `free`, `pro`, `enterprise` |
| daily_limit | integer | `100`, `5000`, or null for enterprise |
| status | text | `active`, `revoked` |
| created_by_user_id | uuid | FK to `users.id`, nullable for system keys |
| last_used_at | timestamptz | Nullable |
| usage_count_today | integer | Daily usage counter |
| usage_window_start | date | Counter window date |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

Indexes:

- Unique index on `key_hash`.
- Indexes on `key_prefix`, `plan`, and `status`.

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

### data_lineage

Tracks real catalog imports for companies, industries, countries, and models.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| entity_type | text | `companies`, `industries`, `countries`, `models` |
| entity_id | uuid | Imported or updated catalog record ID |
| source_id | uuid | FK to `sources.id` |
| source_url | text | Required source URL from CSV |
| source_type | text | Source type used by Confidence Score Engine |
| confidence_score | numeric(5,2) | Calculated import confidence |
| imported_by_user_id | uuid | FK to `users.id` |
| imported_at | timestamptz | Import timestamp |
| import_batch_id | uuid | Groups rows imported from the same CSV |
| action | text | `imported` or `updated` |
| metadata_json | text | Snapshot of imported CSV fields |

Indexes:

- Indexes on `entity_type`, `entity_id`, `source_id`, `source_type`, `imported_by_user_id`, `import_batch_id`, and `action`.

### company_validations

Tracks OpenVals validation status for each company.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| company_id | uuid | Unique FK to `companies.id` |
| status | text | `pending`, `in_review`, `approved`, `rejected` |
| openvals_validation_score | numeric(5,2) | Composite validation score |
| evidence_coverage_score | numeric(5,2) | Evidence tier coverage score |
| confidence_score | numeric(5,2) | Average source credibility score |
| reviewer_notes | text | Nullable reviewer notes |
| reviewed_by_user_id | uuid | FK to `users.id`, nullable |
| approved_by_user_id | uuid | FK to `users.id`, nullable |
| approved_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### company_validation_evidence

Stores source-backed evidence attached to a company validation.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| validation_id | uuid | FK to `company_validations.id` |
| source_id | uuid | FK to `sources.id` |
| evidence_type | text | Source or evidence category |
| coverage_weight | numeric(5,2) | Contribution from source tier |
| review_status | text | `pending`, `approved`, `verified`, `rejected` |
| reviewer_notes | text | Nullable |
| reviewed_by_user_id | uuid | FK to `users.id`, nullable |
| reviewed_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### company_validation_source_reviews

Tracks source review decisions for company validations.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| validation_id | uuid | FK to `company_validations.id` |
| source_id | uuid | FK to `sources.id` |
| review_status | text | `pending`, `approved`, `verified`, `rejected` |
| reviewer_notes | text | Nullable |
| reviewed_by_user_id | uuid | FK to `users.id`, nullable |
| reviewed_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

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

### source_metrics

Stores imported CSV metrics before admin approval.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| company_id | uuid | FK to `companies.id` |
| year | integer | Reporting year |
| metric_type | text | Normalized metric key, example `ai_revenue` |
| value_numeric | numeric(20,6) | Imported value |
| source_id | uuid | FK to `sources.id` |
| source_url | text | Original evidence URL |
| source_type | text | Confidence taxonomy source type |
| confidence_score | numeric(5,2) | Preliminary confidence score |
| methodology_note | text | Extraction or calculation note |
| created_by_user_id | uuid | FK to `users.id` |
| approved_status | text | `pending`, `approved`, `rejected` |
| reviewed_by_user_id | uuid | FK to `users.id`, nullable |
| reviewed_at | timestamptz | Nullable |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

### metric_versions

Captures source metric review and publication history.

| Column | Type | Notes |
| --- | --- | --- |
| id | uuid | Primary key |
| source_metric_id | uuid | FK to `source_metrics.id` |
| metric_value_id | uuid | FK to `metric_values.id`, nullable until approved |
| version | integer | Version number for the imported source metric |
| value_numeric | numeric(20,6) | Versioned value |
| approved_status | text | Status captured by this version |
| created_by_user_id | uuid | FK to `users.id` |
| created_at | timestamptz | Required |
| updated_at | timestamptz | Required |

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
