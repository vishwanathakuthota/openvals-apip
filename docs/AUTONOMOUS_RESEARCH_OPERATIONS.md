# Autonomous Research Operations V1

Status: V1 trust workflow for Microsoft, NVIDIA, and Alphabet/Google.

## Mission

APIP is a trust platform, not a scraping platform. Autonomous Research Operations V1 automates workflow movement while preserving human approval as the publishing gate.

```text
COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH
```

Newly collected information is never automatically published.

## Agents

### Research Agent

Schedule: every 30 minutes through Celery beat task `apip.autonomous_research_agent`.

Purpose: discover new evidence from approved source records only.

Scope:

- Microsoft
- NVIDIA
- Google/Alphabet

Allowed source classes:

- Tier 1: SEC EDGAR, company investor relations pages, earnings calls, annual reports, quarterly reports.
- Tier 2: Reuters, Financial Times, company press releases.
- Tier 3: Stanford AI Index, OECD AI Observatory, IMF, World Bank.

Stored fields:

- Company
- Metric
- Previous value
- Discovered value
- Source URL
- Source type
- Evidence text
- Collection timestamp
- Collection method
- Status: `Collected`

### Validation Agent

Purpose: score collected evidence and move it to review.

Calculates:

- Confidence Score
- Evidence Coverage Score
- Validation Score
- OpenVals Score

Stores:

- Validation timestamp
- Validation notes
- Validation status
- Status: `Under Review`

### Approval Agent

Purpose: recommend action without publishing.

Outcomes:

- Auto Approve
- Manual Review
- Reject

Auto Approve can be recommended only when:

- Source type is `sec_filing`
- Confidence is at least 95
- Evidence Coverage is at least 90

Everything else requires review or rejection. Auto Approve is only a recommendation; it never publishes.

### Publisher Agent

Purpose: publish only reviewer-approved records.

When a record is approved:

- Updates canonical metric values.
- Updates confidence metadata.
- Links sources.
- Writes metric version history.
- Makes lineage visible through public APIs and dashboards.

## Admin Endpoints

- `GET /api/v1/admin/autonomous-research`
- `POST /api/v1/admin/autonomous-research/run/research`
- `POST /api/v1/admin/autonomous-research/run/validation`
- `POST /api/v1/admin/autonomous-research/run/approval`
- `POST /api/v1/admin/autonomous-research/run/publisher`
- `POST /api/v1/admin/autonomous-research/run/all`
- `PATCH /api/v1/admin/autonomous-research/evidence/{record_id}/review`

## Public Endpoints

- `GET /api/v1/trust-center`
- `GET /api/v1/evidence-timeline`
- `GET /api/v1/source-lineage`
- `GET /api/v1/research-queue`
- `GET /api/v1/validation-queue`
- `GET /api/v1/approval-queue`
- `GET /api/v1/publishing-queue`

## Dashboards

- Research Queue
- Validation Queue
- Approval Queue
- Publishing Queue
- Evidence Timeline
- Source Lineage Explorer
- OpenVals Trust Center

Frontend routes:

- Public: `/trust-center`
- Admin: `/admin`
