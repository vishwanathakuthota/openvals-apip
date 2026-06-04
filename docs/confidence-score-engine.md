# Confidence Score Engine

Status: V1 implementation

## Formula

```text
Confidence =
  Source Reliability * 0.40
+ Data Freshness * 0.20
+ Cross Verification * 0.25
+ Methodology Transparency * 0.15
```

## Source Reliability

| Source Type | Score |
| --- | ---: |
| SEC Filing | 100 |
| Annual Report | 95 |
| Earnings Call | 90 |
| Investor Presentation | 80 |
| Analyst Estimate | 70 |
| Industry Report | 65 |
| News Article | 50 |
| Community Estimate | 30 |

## Freshness

| Age | Score |
| --- | ---: |
| Less than 30 days | 100 |
| Less than 90 days | 90 |
| Less than 180 days | 75 |
| Less than 365 days | 60 |
| 365 days or older | 40 |

## Labels

| Score | Label |
| --- | --- |
| 90-100 | Verified |
| 75-89 | High Confidence |
| 60-74 | Medium Confidence |
| 40-59 | Low Confidence |
| 0-39 | Speculative |

## Metric API Contract

Every metric response includes:

- `value`
- `confidence_score`
- `confidence_label`
- `source_count`
- `last_updated`
- `methodology_note`
- `sources`

The nested `confidence` object remains available for UI panels and includes component scores.

## Frontend Behavior

- Dashboard metric cards display confidence score, source count, and last updated.
- Metric cards expose a hover tooltip with value, confidence score, confidence label, source count, and last updated.
- Entity detail pages show the Confidence Score Engine panel and Source Transparency panel.
