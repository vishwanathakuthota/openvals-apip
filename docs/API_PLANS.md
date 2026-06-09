# APIP API Plans

APIP V1 supports four commercial API plans. Plans define daily quota, entitlement access, usage metering, and billing records. Legacy `free` and `pro` values are accepted by the backend and normalized to `community` and `professional`.

## Plans

| Plan | Daily quota | Monthly price | Primary use |
| --- | ---: | ---: | --- |
| Community | 100 requests/day | $0 | Developer trials, demos, and low-volume integrations |
| Research | 1,000 requests/day | $99 | Research teams that need source-backed exports and lineage |
| Professional | 5,000 requests/day | $499 | Production commercial integrations |
| Enterprise | Unlimited | Contract from $2,500/month | Custom terms, SLAs, and high-volume access |

## Entitlements

Community:

- Public API access
- Developer documentation
- Community rate limit

Research:

- Public API access
- Research exports
- Source lineage
- Email support

Professional:

- Public API access
- Research exports
- Source lineage
- Trust Index history
- Priority support

Enterprise:

- Public API access
- Research exports
- Source lineage
- Trust Index history
- Custom contract terms
- SLA hooks

## Rate Limiting

Every public API request must include `X-API-Key`. The backend validates the key, normalizes the plan, increments the daily usage counter, records a usage event, and enforces the plan quota.

Enterprise keys have no fixed daily cap in V1. They are still metered for reporting, abuse detection, and future contract enforcement.

## Admin Operations

Admins can create, rotate, and revoke API keys from `/admin`. Key rotation generates a new plaintext key, resets the daily counter, and keeps the subscription relationship intact. Revocation immediately prevents future public API access.

## Future Payment Integration

V1 stores subscriptions and draft invoices with `payment_provider`, `external_subscription_id`, and `external_invoice_id` fields. These fields are reserved for Stripe, manual invoicing systems, or enterprise billing platforms.
