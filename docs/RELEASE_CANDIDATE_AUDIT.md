# APIP v0.1.0 Beta Release Candidate Audit

Branch: `release/v0.1.0-beta-candidate`

Source candidate: PR #22, `feature/public-beta-launch-prep`

Audit date: June 9, 2026

## Summary

APIP public beta launch prep is close to release candidate quality, but it is not safe to tag as `v0.1.0-beta` yet because two requested API routes are missing:

- `/api/v1/evidence`
- `/api/v1/lineage`

Implemented equivalents exist as `/api/v1/evidence-timeline` and `/api/v1/source-lineage`, but the requested release checklist named the shorter routes. Treat this as a release blocker unless the release checklist is updated to accept the implemented route names.

## Full Local Verification

| Check | Result | Evidence |
| --- | --- | --- |
| `ruff check app --no-cache` | Pass | `All checks passed!` |
| `pytest` | Pass | `47 passed, 1 warning in 136.47s` |
| `npm run lint` | Pass | ESLint completed successfully |
| `npm run build` | Pass | Next.js production build compiled and generated 45 routes |

GitHub Actions for PR #22:

| Check | Result |
| --- | --- |
| `api` | Pass |
| `web` | Pass |

## Production Route Verification

Verified against local production Next server at `http://127.0.0.1:3000`.

| Route | Result |
| --- | --- |
| `/` | 200 |
| `/trust-center` | 200 |
| `/leaderboard` | 200 |
| `/developers` | 200 |
| `/pricing` | 200 |
| `/status` | 200 |
| `/changelog` | 200 |
| `/contact` | 200 |
| `/disclaimer` | 200 |
| `/companies/microsoft` | 200 |
| `/companies/nvidia` | 200 |
| `/companies/alphabet` | 200 |

## API Route Verification

Verified with FastAPI TestClient and seeded test database.

| Route | Result | Notes |
| --- | --- | --- |
| `/api/v1/health` | 200 | Pass |
| `/api/v1/companies` | 200 | Pass with API key |
| `/api/v1/trust-index` | 200 | Pass with API key |
| `/api/v1/evidence` | 404 | Release blocker |
| `/api/v1/lineage` | 404 | Release blocker |
| `/api/v1/evidence-timeline` | 200 | Implemented equivalent |
| `/api/v1/source-lineage` | 200 | Implemented equivalent |

## Beta Signup Verification

| Flow | Result |
| --- | --- |
| Public beta waitlist submission | 202 accepted |
| Enterprise inquiry submission | 202 accepted |
| Invalid beta submission type | 400 rejected |

## Admin Post-Launch Metrics

Verified `GET /api/v1/admin/launch-metrics` after submitting one waitlist and one enterprise inquiry.

Observed payload:

```json
{
  "signups": 1,
  "enterprise_inquiries": 1,
  "api_keys_created": 1,
  "api_usage": {
    "requests_today": 0,
    "total_requests": 0,
    "top_endpoints": []
  },
  "top_endpoints": [],
  "active_plans": {
    "community": 0,
    "research": 0,
    "professional": 0,
    "enterprise": 1
  }
}
```

Result: Pass.

## SEO and Open Graph

Verified these routes expose title, meta description, Open Graph title, and Open Graph image metadata:

- `/`
- `/pricing`
- `/status`
- `/changelog`
- `/contact`
- `/disclaimer`

Result: Pass.

## Public Disclaimer

Verified disclaimer language is visible on:

- `/`
- `/disclaimer`

Required statements are present:

- Data is source-backed.
- Some metrics are estimated or derived.
- Trust Index measures evidence quality, not company quality.

Result: Pass.

## Additional Finding

Attempting to create and seed a standalone SQLite database outside the test harness failed with a unique constraint violation on `metric_sources.metric_value_id, metric_sources.source_id`.

The full `pytest` suite passes because it uses the established test harness, but this should be investigated before relying on standalone SQLite seed verification as a release process.

## Release Decision

Status: Not safe to tag yet.

Do not tag `v0.1.0-beta` until either:

1. Public API aliases are added for `/api/v1/evidence` and `/api/v1/lineage`, or
2. The release checklist is formally updated to use `/api/v1/evidence-timeline` and `/api/v1/source-lineage`.

Recommended next action: create a small release-blocker fix for the API route aliases, then rerun this audit.
