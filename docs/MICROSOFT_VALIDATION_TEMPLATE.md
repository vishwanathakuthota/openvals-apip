# Microsoft Validation Template

Status: Gold Standard Company Validation Workflow for V1 beta.

Report path: `/companies/microsoft/validation-report`

## Purpose

The Microsoft validation workspace is the reference workflow for source-backed company validation in APIP. It validates Microsoft AI economics through section-level source approval, evidence coverage, reviewer notes, lineage snapshots, and methodology traceability.

## Required Evidence Sections

| Section | Required source types | Validation purpose |
| --- | --- | --- |
| Revenue Evidence | `sec_filing`, `annual_report` | Establish audited revenue baseline before AI attribution. |
| AI Revenue Evidence | `annual_report`, `earnings_call`, `investor_presentation` | Track AI-related revenue signals and direct disclosure gaps. |
| AI Investment Evidence | `sec_filing`, `annual_report`, `earnings_call` | Validate AI investment commitments, operating spend, and investment commentary. |
| Infrastructure Investment Evidence | `annual_report`, `earnings_call`, `investor_presentation` | Validate cloud, data center, accelerator, and AI infrastructure investment signals. |
| Earnings Call Evidence | `earnings_call` | Capture management commentary for cross verification. |
| Investor Presentation Evidence | `investor_presentation` | Capture company presentation evidence used to explain AI economics claims. |

## Evidence Coverage Calculation

Each section stores a required source-type checklist. Section coverage is:

```text
approved required source types / total required source types * 100
```

Workspace Evidence Coverage is the average of section coverage scores.

## OpenVals Validation Score

Each section calculates:

```text
Section OpenVals Validation Score =
Evidence Coverage * 45%
+ Source Credibility * 40%
+ Approved Source Ratio * 15%
```

Workspace OpenVals Validation Score is the average of section validation scores.

## Reviewer Notes

Reviewer notes are stored at:

- Workspace level for the overall Microsoft validation report.
- Section level for each required evidence category.
- Evidence-source level for each approved, verified, rejected, or pending source.

## Source Approval Workflow

1. Seed or create the Microsoft validation workspace.
2. Attach required Microsoft source records to each evidence section.
3. Reviewer approves, verifies, or rejects each workspace evidence record.
4. Approved or verified evidence contributes to coverage and validation scoring.
5. Rejected evidence remains visible for auditability and is excluded from approved coverage.

Admin endpoints:

- `GET /api/v1/admin/microsoft-validation`
- `POST /api/v1/admin/microsoft-validation/workspace`
- `PATCH /api/v1/admin/microsoft-validation/evidence/{evidence_id}/review`
- `POST /api/v1/admin/microsoft-validation/export`

## Source Lineage Tracking

Every workspace evidence record stores a lineage snapshot with:

- Source ID
- Source URL
- Source Type
- Source Tier
- Publisher
- Published Date
- Reliability Score
- Credibility Score
- Section Key
- Captured Date

The public report also includes a flattened `source_lineage` array.

## Methodology Traceability

The workspace and every section store methodology trace text. The report page shows:

- Overall Gold Standard v1 methodology.
- Per-section methodology trace.
- Per-evidence methodology trace.
- Source credibility and reliability fields.

## Report Export

The canonical report export is the public route:

- Frontend: `/companies/microsoft/validation-report`
- API: `GET /api/v1/companies/microsoft/validation-report`

The admin export endpoint refreshes the workspace, recalculates scores, updates `exported_at`, writes an audit log, and returns the same report payload.
