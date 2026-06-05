# APIP V1 Real Data Guide

APIP V1 supports real catalog data and financial metric data through admin-only CSV imports. Every imported catalog record stores source attribution, confidence scoring, importer identity, import timestamp, audit events, and data lineage.

## Import Order

Use this order when loading a new real dataset:

1. Countries
2. Companies
3. Industries
4. Models
5. Financial metrics

Companies may reference a headquarters country by `headquarters_country_iso_code`, so countries should exist first. Models may reference a provider by `provider_company_slug`, so companies should exist before model import.

## CSV Templates

Templates live in `samples/`:

- `samples/countries-template.csv`
- `samples/companies-template.csv`
- `samples/industries-template.csv`
- `samples/models-template.csv`
- `samples/financial-metrics-template.csv`

Catalog imports require these common columns:

- `name`
- `source_url`
- `source_type`

Optional source context columns:

- `source_title`
- `publisher`
- `published_at`
- `methodology_note`

Supported `source_type` values align with the Confidence Score Engine:

- `sec_filing`
- `annual_report`
- `earnings_call`
- `investor_presentation`
- `analyst_estimate`
- `industry_report`
- `news_article`
- `community_estimate`

Unknown source types are accepted but receive the lowest reliability score.

## Template-Specific Columns

Countries:

- Required: `name`, `iso_code`, `source_url`, `source_type`
- Optional: `slug`, `region`, `source_title`, `publisher`, `published_at`, `methodology_note`

Companies:

- Required: `name`, `source_url`, `source_type`
- Optional: `slug`, `ticker`, `website_url`, `headquarters_country_iso_code`, `status`, `source_title`, `publisher`, `published_at`, `methodology_note`

Industries:

- Required: `name`, `source_url`, `source_type`
- Optional: `slug`, `status`, `source_title`, `publisher`, `published_at`, `methodology_note`

Models:

- Required: `name`, `model_family`, `source_url`, `source_type`
- Optional: `slug`, `provider_company_slug`, `status`, `source_title`, `publisher`, `published_at`, `methodology_note`

## Admin Import Workflow

Use the admin portal at `/admin`:

1. Sign in with an admin account.
2. Open the ETL section.
3. Select the catalog type: Companies, Industries, Countries, or Models.
4. Upload the matching CSV template.
5. Review the data lineage table for source URL, source type, confidence score, imported by, imported date, and action.
6. Use audit logs to verify the import event history.

Backend endpoints:

- `POST /api/v1/admin/imports/catalog/countries/csv`
- `POST /api/v1/admin/imports/catalog/companies/csv`
- `POST /api/v1/admin/imports/catalog/industries/csv`
- `POST /api/v1/admin/imports/catalog/models/csv`
- `GET /api/v1/admin/lineage`
- `GET /api/v1/admin/lineage?entity_type=companies`

All catalog import endpoints require an admin JWT.

## Validation Rules

The importer validates:

- File extension must be `.csv`.
- Required columns must be present.
- Required cell values cannot be blank.
- `source_url` must start with `http://` or `https://`.
- `website_url`, when provided, must start with `http://` or `https://`.
- `status`, when provided, must be `active` or `archived`.
- Country `iso_code` must be two letters.
- Company `headquarters_country_iso_code`, when provided, must match an existing country.
- Model `provider_company_slug`, when provided, must match an existing company.
- `published_at`, when provided, must be ISO 8601.

Validation errors return `400` with a structured `detail.code` such as `invalid_csv_template` or `invalid_csv_row`.

## Source Attribution Workflow

Each catalog row creates or updates a source record keyed by `source_url`. The source stores:

- `title`
- `source_type`
- `url`
- `publisher`
- `published_at`
- `reliability_score`
- `status`

Catalog import sources are marked `approved` because the workflow is admin-only. Metric imports keep the existing review flow where imported metrics remain pending until approved or rejected.

## Confidence Scoring Integration

Catalog confidence uses the existing Confidence Score Engine:

```text
Confidence =
Source Reliability * 40%
+ Data Freshness * 20%
+ Cross Verification * 25%
+ Methodology Transparency * 15%
```

Catalog imports use one source per row, so cross verification starts at the single-source score. Better source types, recent `published_at` values, and clear `methodology_note` text improve confidence.

## Data Lineage

Every catalog import writes a `data_lineage` row with:

- Entity type
- Entity ID
- Source ID
- Source URL
- Source type
- Confidence score
- Imported by user ID
- Imported date
- Import batch ID
- Action: `imported` or `updated`
- Metadata snapshot from the imported CSV row

This lineage is visible through the admin portal and the `GET /api/v1/admin/lineage` endpoint. Audit logs also record source attachment and catalog import actions.
