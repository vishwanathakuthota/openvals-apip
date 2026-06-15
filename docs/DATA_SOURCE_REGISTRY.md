# APIP Data Source Registry

The data source registry defines approved acquisition targets and source connectors for the public beta real-time data layer.

## Initial Companies

| Company | Slug | Ticker | CIK | Investor Relations |
| --- | --- | --- | --- | --- |
| Microsoft | `microsoft` | `MSFT` | `0000789019` | `https://www.microsoft.com/en-us/Investor` |
| NVIDIA | `nvidia` | `NVDA` | `0001045810` | `https://investor.nvidia.com/` |
| Alphabet | `alphabet` | `GOOGL` | `0001652044` | `https://abc.xyz/investor/` |

## Approved Connectors

### Yahoo Finance

Registry key: `yahoo_finance`

Source type: `market_data`

Purpose:

- Market Cap
- Revenue
- Cash Flow

Retrieval URL pattern:

```text
https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=price,financialData,defaultKeyStatistics
```

### SEC EDGAR

Registry key: `sec_edgar`

Source type: `sec_filing`

Purpose:

- Revenue
- Operating Income
- Cash Flow
- CapEx
- EPS

Retrieval URL pattern:

```text
https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json
```

SEC requests include an APIP user agent:

```text
OpenVals APIP beta data acquisition contact@openvalidations.com
```

### Company Investor Relations

Registry key: `investor_relations`

Source type: `investor_relations`

Purpose:

- Source availability monitoring
- Investor relations retrieval timestamp
- Company source lineage

Investor relations pages are tracked as source evidence even when no metric is parsed from the page.

## Metric Registry

| Metric key | Display name | Unit |
| --- | --- | --- |
| `revenue` | Revenue | `usd` |
| `market_cap` | Market Cap | `usd` |
| `operating_income` | Operating Income | `usd` |
| `cash_flow` | Operating Cash Flow | `usd` |
| `capex` | Capital Expenditure | `usd` |
| `eps` | Diluted EPS | `usd_per_share` |

## Lineage Requirements

Every acquired metric stores:

- Source URL
- Source type
- Publisher
- Published date when available
- Retrieval timestamp
- Freshness score
- Methodology note
- Confidence score

## Expansion Rules

New sources may be added only when they support APIP trust principles:

- Source-backed metrics
- Reproducible retrieval
- Clear methodology
- Persisted lineage
- Confidence score compatibility
