# Trust Center

The Trust Center is the public control room for APIP trust operations. It explains how evidence moves from collection to publication and exposes the current platform-level OpenVals Trust Index.

## Public Route

Frontend route:

- `/trust-center`

Backend route:

- `GET /api/v1/trust-center`

## Workflow

APIP follows this workflow:

`COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH`

Newly collected information is never automatically published. Public users only see records that completed reviewer approval and publication.

## Trust Center Data

The Trust Center displays:

- Evidence record totals.
- Under-review and published counts.
- Manual review counts.
- Global Trust Index.
- Trust trend snapshots.
- Trust change notifications.
- Evidence timeline.
- Source lineage.
- Methodology summary.

## Trust Index Summary

The Trust Center includes the current global Trust Index summary:

- Score.
- Rating.
- Classification.
- Component scores.
- Distinct source count.
- Published record count.
- Methodology version.

## Evidence Timeline

The evidence timeline shows each evidence record with:

- Company.
- Metric.
- Evidence classification.
- Validation status.
- Confidence.
- Evidence coverage.
- OpenVals score.
- Source type and URL.

## Source Lineage

Every public metric must be traceable to approved source lineage. The public lineage contract includes:

- Source URL.
- Source type.
- Collection date.
- Confidence.
- Evidence coverage.
- Reviewer.
- Approval date.

## Operational Rules

- Research agents collect evidence only.
- Validation agents score evidence only.
- Approval agents recommend actions only.
- Publisher agents publish approved records only.
- Human approval is required before public publication.
