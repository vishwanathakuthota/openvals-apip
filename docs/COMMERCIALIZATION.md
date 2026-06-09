# Commercialization Foundation

APIP Sprint 4 prepares the platform for monetization while preserving the trust-first product model. Commercial controls must never change validation outcomes, confidence scores, source lineage, or published metrics.

## Scope

The V1 commercial foundation includes:

- API key lifecycle management
- Usage metering by key, endpoint, method, plan, and date
- Rate limiting for Community, Research, Professional, and Enterprise plans
- Subscription records tied to API keys
- Draft invoice records for future billing integration
- Developer portal pricing and documentation
- Admin revenue, active-user, API-consumption, and plan-distribution reporting

## Data Model

Commercial records are intentionally small and auditable:

- `api_keys`: public API credentials, plan, status, usage window, and daily counter
- `api_usage_events`: one metering event per authenticated public API request
- `api_subscriptions`: active plan, quota, entitlements, billing period, and payment hook fields
- `invoices`: draft invoice records for each subscription billing period

## Request Flow

1. Client sends `X-API-Key`.
2. Backend validates the key hash and active status.
3. Backend normalizes legacy plan names if needed.
4. Backend enforces the daily quota.
5. Backend records an `api_usage_events` row.
6. Public API route returns the requested trust, metric, or catalog payload.

Missing, invalid, revoked, or over-quota keys receive authentication or rate-limit errors before route execution.

## API Key Lifecycle

Admins can:

- Create a key with a plan.
- Rotate a key to issue a new plaintext secret.
- Revoke a key to block access.
- Update the plan, which also updates the subscription entitlement snapshot.

Plaintext keys are only returned at create and rotate time. The database stores only the hash and prefix.

## Admin Dashboard Metrics

The admin portal exposes:

- Monthly recurring revenue from active subscription records
- Draft invoice amount
- Active API keys
- Active subscriptions
- Requests today
- Total requests
- Top endpoints by request count
- Plan distribution

These metrics are operational indicators. They are not a financial ledger.

## Billing Hooks

Payment processing is not implemented in V1. The billing foundation stores provider and external ID fields so a later sprint can attach Stripe, invoice-system, or enterprise contract workflows without changing the API key model.

## Guardrails

- Commercial status must not influence confidence scoring.
- Commercial status must not hide lineage from public records returned under the plan's entitlement rules.
- Usage metering records only operational metadata and must not store plaintext API keys.
- Revoked keys remain visible to admins for auditability.
