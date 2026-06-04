# ETL and Source Management

APIP V1 imports financial metrics from analyst-provided CSV files, stores them as pending source evidence, and publishes them only after administrator approval.

## CSV Template

Use [samples/financial-metrics-template.csv](../samples/financial-metrics-template.csv).

Required columns:

- `company`
- `year`
- `metric_type`
- `value`
- `source_url`
- `source_type`

Optional columns:

- `methodology_note`
- `publisher`
- `published_at`

Supported `source_type` values follow the Confidence Score Engine taxonomy: `sec_filing`, `annual_report`, `earnings_call`, `investor_presentation`, `analyst_estimate`, `industry_report`, `news_article`, and `community_estimate`.

## Import Flow

1. Admin uploads a CSV through `POST /api/v1/admin/imports/csv`.
2. Each row is validated and stored in `source_metrics` with `approved_status = pending`.
3. A `sources` record is created with reliability scoring from the Confidence Score Engine.
4. A `metric_versions` row captures the pending version.
5. An `audit_logs` row records the import event.

## Approval Flow

Admin approval through `PATCH /api/v1/admin/source-metrics/{id}/approve` publishes the imported evidence into canonical APIP metrics:

- Creates or updates the matching `metric_definitions` record.
- Creates or updates the canonical company `metric_values` row for the imported year.
- Links approved evidence through `metric_sources`.
- Recalculates and stores `confidence_scores`.
- Updates `sources.status` and `source_metrics.approved_status` to `approved`.
- Records publication and approval events in `audit_logs`.

Admin rejection through `PATCH /api/v1/admin/source-metrics/{id}/reject` marks the source and source metric as rejected, writes a metric version, and keeps the data out of public metric responses.

## Admin UI

The Next.js admin portal includes:

- CSV upload
- Imported metric review
- Approve/reject actions
- Audit log timeline

The browser signs in through the Next.js admin login proxy and stores the returned admin JWT in session storage. Internal Next.js admin routes forward that JWT to FastAPI admin APIs, so admin controls are hidden until login and all mutations still enforce FastAPI role-based authorization.
