# Trust and Validation Model

APIP V1 separates evidence collection from publication. The system can collect, score, and recommend actions, but public metrics change only after human approval.

## Core Rule

```text
Collected evidence cannot become public until reviewed, approved, and published.
```

## Confidence Engine

```text
Confidence =
Source Reliability * 40%
+ Data Freshness * 20%
+ Cross Verification * 25%
+ Methodology Transparency * 15%
```

Labels:

- 90-100: Verified
- 75-89: High Confidence
- 60-74: Medium Confidence
- 40-59: Low Confidence
- 0-39: Speculative

## Evidence Coverage Score

```text
Coverage =
Required Evidence Found / Required Evidence Expected
```

Displayed as 0-100%.

## Human Review Workflow

Reviewer actions:

- Approve
- Reject
- Modify Confidence
- Add Notes
- Request Additional Evidence

Stored fields:

- Reviewer
- Timestamp
- Decision
- Notes

## Source Lineage

Every public metric can expose:

- Source URL
- Source Type
- Collection Date
- Confidence
- Evidence Coverage
- Reviewer
- Approval Date

This lets users trace where a number came from, why it was published, its confidence level, validation status, and reviewer approval history.

## Phase 1 Scope

Autonomous Research Operations V1 covers:

- Microsoft
- NVIDIA
- Google/Alphabet

The scope intentionally does not expand company coverage.
