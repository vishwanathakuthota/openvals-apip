# Microsoft Gold Standard Review

Status: Gold Standard Company #1

Branch: `feature/microsoft-gold-standard`

## Objective

Microsoft is the first APIP company completed through the Gold Standard workflow. The workflow verifies that every public Microsoft company metric has evidence, lineage, confidence, evidence coverage, OpenVals Score, reviewer approval, and publication history.

## Generated Public Outputs

- `/companies/microsoft/validation-report`
- `/companies/microsoft/trust-report`
- `/companies/microsoft/evidence-timeline`
- `/companies/microsoft/source-lineage`
- `/companies/microsoft/openvals-score`

## Gold Standard Metric Scope

The Microsoft Gold Standard review covers all seeded Microsoft company metrics for V1:

| Metric | Evidence | Lineage | Confidence | Coverage | OpenVals Score | Approval | Publication |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AI Revenue | Required | Required | Required | Required | Required | Required | Required |
| AI Spend | Required | Required | Required | Required | Required | Required | Required |
| ROI | Required | Required | Required | Required | Required | Required | Required |
| Revenue Growth | Required | Required | Required | Required | Required | Required | Required |
| Gross Margin | Required | Required | Required | Required | Required | Required | Required |
| Adoption | Required | Required | Required | Required | Required | Required | Required |

## Evidence Sources

Microsoft Gold Standard evidence is drawn from the approved source registry:

- Microsoft SEC company filing registry
- Microsoft 2025 Annual Report
- Microsoft earnings releases and webcasts archive
- Microsoft investor events and presentations archive

The evidence coverage engine checks required source types per metric. Microsoft coverage includes SEC filing evidence, annual report evidence, earnings call evidence, and investor presentation evidence where required by the metric.

## Workflow Completion

Microsoft follows the APIP trust workflow:

```text
COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH
```

Completion checks:

- Research Agent collected Microsoft evidence records for all six Gold Standard metrics.
- Validation Agent calculated Confidence Score, Evidence Coverage Score, Validation Score, and OpenVals Score.
- Approval Agent generated review recommendations without publishing automatically.
- APIP Admin approved the Microsoft records.
- Publisher Agent published only approved Microsoft records.
- Published metric values were updated with `Validated` evidence classification and `Published` validation status.
- Public metric responses expose source count, confidence, coverage, OpenVals Score, last updated, methodology note, and lineage.

## Validation Workspace Completion

The Microsoft validation workspace includes six required evidence sections:

- Revenue Evidence
- AI Revenue Evidence
- AI Investment Evidence
- Infrastructure Investment Evidence
- Earnings Call Evidence
- Investor Presentation Evidence

The public validation report is marked:

```text
Gold Standard Company #1
```

The workspace status is `gold_standard` when all section coverage and validation scores are complete.

## Audit Verification

Automated API coverage verifies:

- `/api/v1/companies/microsoft/validation-report` returns Gold Standard status and all required sections.
- `/api/v1/companies/microsoft/trust-report` returns six published Microsoft evidence records.
- `/api/v1/companies/microsoft/evidence-timeline` exposes collection, validation, approval, and publication timestamps.
- `/api/v1/companies/microsoft/source-lineage` exposes public lineage for published metrics.
- `/api/v1/companies/microsoft/openvals-score` returns Gold Standard metadata and company score.
- `/api/v1/metrics/search` confirms every Microsoft metric has confidence, coverage, OpenVals Score, sources, and source lineage.

## Result

Microsoft is the first fully validated Gold Standard company in APIP. Users can click into Microsoft metrics and trace where each number came from, why it was published, how confidence and coverage were calculated, and who approved publication.
