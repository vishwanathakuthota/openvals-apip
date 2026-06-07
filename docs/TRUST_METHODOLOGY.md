# Trust Methodology

OpenVals Trust Methodology defines how APIP turns source-backed evidence into a public trust score.

## Methodology Version

Current version:

- `trust-index-v1`

## Components

### Confidence

Weight: 30%

Confidence measures reliability of a metric using source reliability, freshness, cross verification, and methodology transparency.

### Evidence Coverage

Weight: 25%

Evidence Coverage measures how much required evidence exists for a metric or company compared with the expected evidence baseline.

### Transparency

Weight: 20%

Transparency measures whether APIP can explain:

- Where the number came from.
- Which source supported it.
- How it was collected.
- How it was scored.
- Why it was approved.

### Reproducibility

Weight: 15%

Reproducibility measures whether an analyst can independently follow the method, source trail, and calculation path to reproduce the published result.

### Source Quality

Weight: 10%

Source Quality measures the credibility of source types and publishers. Tier 1 sources such as SEC filings, annual reports, quarterly reports, and earnings call materials carry the highest source quality.

## Formula

`Trust Index = Confidence * 0.30 + Evidence Coverage * 0.25 + Transparency * 0.20 + Reproducibility * 0.15 + Source Quality * 0.10`

## Publication Contract

A metric can appear publicly only when:

- It has source-backed evidence.
- It has confidence and coverage scores.
- It has source lineage.
- It has reviewer approval history.
- It has publication status.

## Methodology Pages

Frontend routes:

- `/trust-index`
- `/trust-center`
- `/trust-methodology`
- `/leaderboard`

These pages expose the Trust Index score, leaderboard, trend history, notifications, and scoring methodology.

## Auditability

Trust Index snapshots are stored with the methodology version so historical values remain explainable if the methodology changes in future versions.
