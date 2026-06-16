# AI Profitability Score

The AI Profitability Score measures whether a company appears to convert AI investment into durable economic output.

## Formula

AI Profitability Score =

- 25% Revenue Efficiency
- 20% AI Revenue Growth
- 20% AI Margin Proxy
- 20% Infrastructure ROI
- 15% Capital Efficiency

Scores are normalized to a 0-100 range.

## Components

Revenue Efficiency compares estimated AI revenue against estimated AI investment.

AI Revenue Growth measures estimated growth in AI revenue evidence.

AI Margin Proxy reflects available margin and operating leverage evidence for AI-related revenue.

Infrastructure ROI compares estimated AI revenue against infrastructure-heavy spend.

Capital Efficiency compares estimated AI revenue against total revenue context.

## Ratings

- A: 85-100
- B: 75-84
- C: 65-74
- D: 50-64
- F: 0-49

## API Output

`GET /api/v1/ai-profitability` returns a ranked leaderboard with:

- Score
- Rating
- Classification
- Component scores
- Confidence score
- Source count
- Last updated
- Sources
- Methodology note
