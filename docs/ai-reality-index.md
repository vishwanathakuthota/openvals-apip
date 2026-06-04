# AI Reality Index

The AI Reality Index is APIP's V1 composite score for real-world AI profitability.

## Formula

```text
AI Reality Index = (ROI * 0.4) + (Revenue Growth * 0.3) + (Margin * 0.2) + (Adoption * 0.1)
```

Each component is normalized to a `0-100` score before the weighted calculation. Ratio-style metric values such as `0.74` are interpreted as `74`.

## Classifications

| Score | Classification |
| --- | --- |
| 90-100 | Elite |
| 70-89 | Strong |
| 50-69 | Emerging |
| 30-49 | Speculative |
| 0-29 | Cash Burn Zone |

## Backend Flow

`GET /api/v1/ai-reality-index` calculates ranked company, industry, and country index records from approved metric values:

- `roi`
- `revenue_growth`
- `gross_margin`, `net_margin`, or `margin`
- `adoption`

Entities missing any required component are excluded from the ranking until approved source-backed metrics are available. Each response includes component scores, classification, confidence score, source count, last updated timestamp, and methodology note.

## Frontend Flow

The dashboard and dedicated AI Reality Index page display:

- AI Reality Index score card
- Leaderboard
- Classification badges
- Explanation modal with the formula and classification bands
