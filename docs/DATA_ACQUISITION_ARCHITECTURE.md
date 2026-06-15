# Real-Time Data Acquisition Architecture

Sprint 6 introduces the APIP real-time data acquisition layer for continuously refreshed company metrics.

## Goals

- Replace placeholder company financial metrics with source-backed refreshed data.
- Refresh Microsoft, NVIDIA, and Alphabet first.
- Preserve source lineage, retrieval timestamps, and freshness scores.
- Update existing company dashboards automatically through the current `MetricValue` API path.

## Sources

Initial connectors:

- Yahoo Finance
- SEC EDGAR company facts
- Company Investor Relations pages

## Refresh Cadence

The Celery beat schedule runs:

```text
apip.refresh_company_metrics every 1800 seconds
```

This is a 30-minute cadence. The admin API can also trigger a refresh:

```text
POST /api/v1/admin/data-acquisition/refresh
```

Status is available at:

```text
GET /api/v1/admin/data-acquisition/status
```

## Data Flow

1. Scheduler triggers `apip.refresh_company_metrics`.
2. The acquisition service loads target companies from the source registry.
3. Connectors retrieve source data.
4. Parsed metrics are normalized into APIP metric keys.
5. Sources are upserted with `retrieved_at` and `freshness_score`.
6. Metrics are upserted into `metric_values`.
7. Lineage is stored through `metric_sources` and `source_metrics`.
8. Confidence scores are recalculated using source reliability, freshness, cross-verification, and methodology transparency.
9. Company dashboards read updated metrics through existing public APIs.

## Metrics

Initial refreshed metrics:

- Revenue
- Market Cap
- Operating Income
- Cash Flow
- CapEx
- EPS

## Persistence

The layer writes to existing trust and metric tables:

- `sources`
- `source_metrics`
- `metric_values`
- `metric_sources`
- `confidence_scores`

New operational run tracking:

- `data_acquisition_runs`

New source and source metric fields:

- `retrieved_at`
- `freshness_score`

## Freshness Scoring

Freshness uses the existing Confidence Score Engine freshness model:

- Less than 30 days: 100
- Less than 90 days: 90
- Less than 180 days: 75
- Less than 365 days: 60
- Older or missing: 40

## Publication Model

Sprint 6 updates approved public dashboard metrics automatically from approved data sources. The layer does not bypass APIP source lineage or confidence scoring. Each refreshed number remains traceable to source URL, source type, retrieval timestamp, and freshness score.

## Failure Handling

Every connector run records:

- Target company
- Connector name
- Source name
- Status
- Start and completion timestamps
- Retrieval timestamp
- Records found
- Error message when failed

Failures are isolated per connector and company so one source outage does not block other source refreshes.
