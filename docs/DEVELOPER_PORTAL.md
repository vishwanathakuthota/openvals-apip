# Developer Portal

The APIP developer portal at `/developers` is the public entry point for API access, examples, pricing, and authentication guidance.

## Audience

The page is designed for:

- Developers evaluating APIP data access
- Researchers integrating trust and validation metrics
- Commercial teams comparing plan tiers
- Enterprise prospects reviewing quota and support expectations

## Authentication

All public API examples use:

```text
X-API-Key: apip_live_...
```

API keys are created by admins in the admin portal. Plaintext keys are visible only during creation and rotation.

## Examples

The developer portal includes examples for:

- Companies
- Industries
- Metrics
- Confidence
- AI Reality Index
- Trust Index
- Source lineage

All examples target the production domain:

```text
https://apip.openvalidations.com
```

## Pricing

The portal displays Community, Research, Professional, and Enterprise tiers with quota, price, and entitlement positioning. Pricing copy should stay aligned with `docs/API_PLANS.md`.

## Admin Dependencies

The portal itself is public, but key issuance is protected:

- Admin login is required at `/admin`.
- Admins can create, rotate, revoke, and update keys.
- Usage and subscription data are visible only in the admin portal.

## Launch Checklist

Before publishing the developer portal:

- Confirm `/api/v1/health` returns healthy behind the production domain.
- Confirm public API routes reject missing keys.
- Confirm a Community key is limited to 100 requests per day.
- Confirm a Professional key allows 5,000 requests per day.
- Confirm usage events are recorded after public API calls.
- Confirm rotated keys immediately replace the old key material.
- Confirm revoked keys return unauthorized responses.
