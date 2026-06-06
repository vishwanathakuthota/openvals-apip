# Microsoft Case Study

Status: End-to-End Validation Pilot for APIP V1.

Target company: Microsoft

## Objective

Microsoft is the first company validated through the full APIP trust workflow:

```text
COLLECT -> ANALYZE -> SCORE -> QUEUE -> REVIEW -> APPROVE -> PUBLISH
```

The pilot proves that APIP can collect evidence, score it, submit it to review, approve it, publish it, and expose public lineage without automatically publishing newly collected information.

## Pilot Flow

1. Research Agent collects Microsoft evidence from approved source registry records.
2. Evidence is stored in `autonomous_evidence_records` with status `Collected`.
3. Validation Agent calculates confidence, evidence coverage, validation score, and OpenVals Score.
4. Approval Agent recommends review action.
5. APIP Admin approves Microsoft pilot evidence.
6. Publisher Agent publishes approved Microsoft records.
7. Public metric payloads expose classification, validation status, OpenVals Score, confidence, coverage, source count, and lineage.

## Generated Outputs

- `/companies/microsoft/validation-report`
- `/companies/microsoft/evidence-timeline`
- `/companies/microsoft/source-lineage`
- `/companies/microsoft/openvals-score`
- `/companies/microsoft/trust-report`

## Evidence Stored

Each Microsoft evidence record stores:

- Company
- Metric
- Previous value
- Discovered value
- Source URL
- Source type
- Evidence text
- Collection timestamp
- Collection method
- Confidence Score
- Evidence Coverage Score
- Validation Score
- OpenVals Score
- Reviewer decision
- Reviewer notes
- Approval date
- Publication date

## Engines Used

### Confidence Engine

```text
Confidence =
Source Reliability * 40%
+ Data Freshness * 20%
+ Cross Verification * 25%
+ Methodology Transparency * 15%
```

### Evidence Coverage Engine

```text
Coverage =
Required Evidence Found / Required Evidence Expected
```

### OpenVals Score Engine

```text
OpenVals Score =
Confidence * 30%
+ Evidence Coverage * 25%
+ Transparency * 20%
+ Reproducibility * 15%
+ Source Quality * 10%
```

## Publication Rule

The pilot keeps the core APIP rule intact:

```text
No newly collected evidence becomes public until a reviewer approves it and the Publisher Agent releases it.
```

## Result

Microsoft becomes the first fully validated APIP company. Users can inspect where Microsoft metrics came from, why they were published, their confidence level, validation status, source lineage, and reviewer approval history.
