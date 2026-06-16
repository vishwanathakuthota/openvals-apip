# Live Data Ingestion

APIP live ingestion refreshes public market and filing data from free sources. It is separate from seed data and is designed to update company dashboards with source-backed records.

## Audit Findings

Before this implementation:

- Yahoo Finance / `yfinance` was not used.
- SEC EDGAR company facts or submissions ingestion was not used.
- Docker had a worker container, but no production scheduler running every 30 minutes.
- There was no `/api/v1/ingestion/status` health/status endpoint.
- There was no `/admin/ingestion` page or manual ingestion trigger.

## Sources

### Yahoo Finance

- Library: `yfinance`
- API key: not required
- Enabled by: `YAHOO_FINANCE_ENABLED=true`
- Metrics:
  - market cap
  - stock price
  - revenue
  - operating income
  - cash flow
  - capex
  - EPS

### SEC EDGAR

- Endpoints:
  - `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`
  - `https://data.sec.gov/submissions/CIK##########.json`
- API key: not required
- Required header: `SEC_USER_AGENT`
- Metrics:
  - revenue
  - operating income
  - cash flow
  - capex
  - EPS
  - 10-K / 10-Q filing metadata

## Stored Fields

Each live record stores:

- company
- symbol
- metric type
- value
- currency
- source URL
- source type
- retrieved timestamp
- freshness score
- confidence score
- raw payload snapshot
- raw payload hash
- ingestion status
- SEC filing accession, form, and period end where available

## Scheduler

Celery Beat schedules:

```text
task: apip.ingest_live_data
interval: INGESTION_INTERVAL_MINUTES * 60
default: 30 minutes
```

Docker services:

- `worker`: executes ingestion jobs.
- `scheduler`: runs Celery Beat and logs every scheduled dispatch.

Production Compose includes the `scheduler` service so ingestion cadence is visible in container logs.

## Manual Trigger

Admin endpoint:

```http
POST /api/v1/admin/ingestion/run
Authorization: Bearer <admin_jwt>
```

Admin UI:

```text
/admin/ingestion
```

## Status Endpoint

Public read-only status:

```http
GET /api/v1/ingestion/status
```

Returns:

- enabled state
- Yahoo Finance enabled state
- SEC enabled state
- scheduler task name
- interval minutes
- last run
- recent live records

## Current Company Targets

V1 live ingestion targets public companies with free market and SEC coverage:

- Microsoft: `MSFT`, CIK `789019`
- NVIDIA: `NVDA`, CIK `1045810`
- Alphabet: `GOOGL`, CIK `1652044`
- Meta: `META`, CIK `1326801`
- Amazon: `AMZN`, CIK `1018724`

Private AI companies remain eligible for manual source registry workflows until trusted free live sources are available.

## Verification

Automated tests cover:

- Yahoo connector normalization from mocked `yfinance` responses.
- SEC connector normalization from mocked company facts and submissions responses.
- Celery Beat 30-minute scheduler configuration.
- `/api/v1/ingestion/status`.

Run:

```bash
cd services/api
ruff check app --no-cache
python -m pytest
```
