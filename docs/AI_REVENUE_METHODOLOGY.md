# AI Revenue Methodology

APIP estimates AI revenue from approved evidence records rather than unsourced market narratives.

## Inputs

- Company revenue context
- Earnings call disclosures
- Investor presentations
- SEC filings and annual reports
- Public AI product, cloud, infrastructure, and adoption disclosures

## Estimate Workflow

1. Collect source-backed evidence for each company.
2. Normalize evidence to the active reporting period.
3. Map evidence to AI revenue-bearing business lines.
4. Apply the company disclosure profile.
5. Calculate confidence from source reliability, freshness, cross verification, and methodology transparency.
6. Publish the estimate only with source count, confidence score, trust score, last updated, and methodology note.

## API Output

`GET /api/v1/ai-revenue` returns one record per tracked company with:

- AI Revenue Estimate
- Input revenue
- AI revenue share
- Confidence
- Trust
- Source count
- Sources
- Last updated
- Methodology note

## V1 Company Scope

- Microsoft
- NVIDIA
- Alphabet
- Meta
- Amazon
- OpenAI
- Anthropic
- xAI
- Mistral
- Perplexity
