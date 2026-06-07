# NVIDIA Gold Standard Review

Status: Gold Standard Company #2

Branch: `feature/nvidia-gold-standard`

## Objective

NVIDIA is the second APIP company completed through the Gold Standard workflow. The workflow verifies that every public NVIDIA company metric has evidence, lineage, confidence, evidence coverage, OpenVals Score, reviewer approval, and publication history.

## Generated Public Outputs

- `/companies/nvidia/validation-report`
- `/companies/nvidia/trust-report`
- `/companies/nvidia/evidence-timeline`
- `/companies/nvidia/source-lineage`
- `/companies/nvidia/openvals-score`

## Gold Standard Metric Scope

The NVIDIA Gold Standard review covers all seeded NVIDIA company metrics for V1:

| Metric | Evidence | Lineage | Confidence | Coverage | OpenVals Score | Approval | Publication |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AI Revenue | Required | Required | Required | Required | Required | Required | Required |
| AI Spend | Required | Required | Required | Required | Required | Required | Required |
| ROI | Required | Required | Required | Required | Required | Required | Required |
| Revenue Growth | Required | Required | Required | Required | Required | Required | Required |
| Gross Margin | Required | Required | Required | Required | Required | Required | Required |
| Adoption | Required | Required | Required | Required | Required | Required | Required |

## Evidence Sources

NVIDIA Gold Standard evidence is drawn from the approved source registry:

- NVIDIA SEC company filing registry
- NVIDIA FY2025 Annual Report
- NVIDIA quarterly results and earnings call archive
- NVIDIA investor events and presentations archive

The evidence coverage engine checks required source types per metric. NVIDIA coverage includes SEC filing evidence, annual report evidence, earnings call evidence, and investor presentation evidence where required by the metric.

## Workflow Completion

NVIDIA follows the APIP trust workflow:

```text
COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH
```

Completion checks:

- Research Agent collected NVIDIA evidence records for all six Gold Standard metrics.
- Validation Agent calculated Confidence Score, Evidence Coverage Score, Validation Score, and OpenVals Score.
- Approval Agent generated review recommendations without publishing automatically.
- APIP Admin approved the NVIDIA records.
- Publisher Agent published only approved NVIDIA records.
- Published metric values were updated with `Validated` evidence classification and `Published` validation status.
- Public metric responses expose source count, confidence, coverage, OpenVals Score, last updated, methodology note, and lineage.

## Validation Workspace Completion

The NVIDIA validation workspace includes six required evidence sections:

- Revenue Evidence
- AI Revenue Evidence
- AI Investment Evidence
- Infrastructure Investment Evidence
- Earnings Call Evidence
- Investor Presentation Evidence

The public validation report is marked:

```text
Gold Standard Company #2
```

The workspace status is `gold_standard` when all section coverage and validation scores are complete.

## Audit Verification

Automated API coverage verifies:

- `/api/v1/companies/nvidia/validation-report` returns Gold Standard status and all required sections.
- `/api/v1/companies/nvidia/trust-report` returns six published NVIDIA evidence records.
- `/api/v1/companies/nvidia/evidence-timeline` exposes collection, validation, approval, and publication timestamps.
- `/api/v1/companies/nvidia/source-lineage` exposes public lineage for published metrics.
- `/api/v1/companies/nvidia/openvals-score` returns Gold Standard metadata and company score.
- `/api/v1/metrics/search` confirms every NVIDIA metric has confidence, coverage, OpenVals Score, sources, and source lineage.

## Result

NVIDIA is the second fully validated Gold Standard company in APIP. Users can click into NVIDIA metrics and trace where each number came from, why it was published, how confidence and coverage were calculated, and who approved publication.
