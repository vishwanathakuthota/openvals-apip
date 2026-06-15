# Data Source Keys

APIP V1 live ingestion uses free public sources and does not require paid data keys.

## Required Environment Variables

### SEC_USER_AGENT

Required for SEC EDGAR requests.

Example:

```bash
SEC_USER_AGENT="OpenVals APIP admin@openvalidations.com"
```

The SEC expects automated clients to identify themselves with a meaningful User-Agent that includes contact information.

### YAHOO_FINANCE_ENABLED

Enables Yahoo Finance ingestion through `yfinance`.

Default:

```bash
YAHOO_FINANCE_ENABLED=true
```

### INGESTION_INTERVAL_MINUTES

Controls the Celery Beat cadence.

Default:

```bash
INGESTION_INTERVAL_MINUTES=30
```

## No API Key Required

No key is required for:

- Yahoo Finance via `yfinance`
- SEC EDGAR company facts API
- SEC EDGAR submissions API

## Operational Notes

- SEC ingestion must set `SEC_USER_AGENT` in local and production environments.
- Production Docker Compose runs a dedicated `scheduler` service.
- Manual ingestion trigger is admin-protected at `/admin/ingestion`.
