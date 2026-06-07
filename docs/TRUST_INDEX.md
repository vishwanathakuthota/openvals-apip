# OpenVals Trust Index

The OpenVals Trust Index is the primary trust metric for APIP. It summarizes whether a published company, metric, or platform-level result is backed by credible evidence, transparent methodology, reproducible calculations, and approved source lineage.

## Formula

Trust Index =

- Confidence x 30%
- Evidence Coverage x 25%
- Transparency x 20%
- Reproducibility x 15%
- Source Quality x 10%

All component scores use a 0-100 scale. The final Trust Index is rounded to two decimal places.

## Outputs

Each Trust Index response generates:

- `trust_index`: numeric score from 0-100.
- `trust_rating`: reader-facing rating.
- `trust_classification`: evidence maturity classification.
- `components`: weighted inputs used in the calculation.
- `source_count`: distinct source count.
- `published_record_count`: approved and published evidence count.
- `methodology_version`: current methodology identifier.

## Ratings

| Score | Trust Rating | Trust Classification |
| --- | --- | --- |
| 90-100 | Verified | Gold Standard |
| 80-89 | High Trust | Strong Evidence |
| 70-79 | Trusted | Reliable |
| 60-69 | Watchlist | Developing |
| 0-59 | Low Trust | Insufficient Evidence |

## API Surface

The Trust Index is available through:

- `GET /api/v1/trust-index`
- `GET /api/v1/leaderboard`
- `GET /api/v1/trust-methodology`
- `GET /api/v1/trust-center`
- `GET /api/v1/companies`
- `GET /api/v1/companies/{id}`
- `GET /api/v1/metrics/search`

Company payloads include a `trust_index` object. Metric payloads include `trust_index`, `trust_rating`, and `trust_classification` fields alongside confidence, coverage, sources, and lineage.

## Historical Tracking

APIP stores Trust Index snapshots in `trust_index_snapshots`. Snapshots support:

- Historical trust trend charts.
- Entity-level trust history.
- Change detection between snapshots.
- Auditability of methodology version over time.

## Trust Change Notifications

APIP stores Trust Index change notifications in `trust_change_notifications`. Notifications are generated when current Trust Index values are compared with the latest prior snapshot. They include:

- Entity name and type.
- Previous and current Trust Index.
- Change amount.
- Notification type.
- Message.
- Status.

Notifications are informational. They do not publish or modify evidence by themselves.
