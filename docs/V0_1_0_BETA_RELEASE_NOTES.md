# APIP v0.1.0-beta Release Notes

Status: Release candidate pending blocker resolution

Target tag: `v0.1.0-beta`

Target domain: `https://apip.openvalidations.com`

## Overview

APIP v0.1.0-beta is the first public beta candidate for the OpenVals AI Profitability Intelligence Platform. The release positions APIP as a trust platform for AI profitability intelligence, combining source-backed metrics, confidence scoring, evidence coverage, Trust Index methodology, and public API access.

## Highlights

- Public beta landing page with OpenVals positioning.
- Beta waitlist and enterprise inquiry capture.
- Public disclaimer covering source-backed data, estimated metrics, and Trust Index scope.
- Changelog, status, pricing, contact, developers, methodology, Trust Center, and disclaimer pages.
- Public API key management foundation.
- Usage metering and plan-based rate-limit foundation.
- Admin post-launch metrics dashboard.
- Gold Standard validation coverage for Microsoft, NVIDIA, and Alphabet.
- Expanded AI economy company coverage.
- Trust Center, Trust Index, AI Reality Index, source lineage, and validation reports.

## Public Beta Pages

- `/`
- `/trust-center`
- `/leaderboard`
- `/developers`
- `/pricing`
- `/status`
- `/changelog`
- `/contact`
- `/disclaimer`
- `/companies/microsoft`
- `/companies/nvidia`
- `/companies/alphabet`

## API Surface

Verified routes:

- `/api/v1/health`
- `/api/v1/companies`
- `/api/v1/trust-index`
- `/api/v1/evidence-timeline`
- `/api/v1/source-lineage`

Release blocker routes:

- `/api/v1/evidence`
- `/api/v1/lineage`

These two routes returned 404 during release-candidate verification. They should be added as aliases or the release checklist should be updated before tagging.

## Commercial Foundation

V0.1.0-beta includes:

- API key create, rotate, and revoke.
- Community, Research, Professional, and Enterprise plans.
- Usage metering by endpoint, method, key, plan, and date.
- Subscription and invoice records for future billing integration.
- Developer portal API examples and pricing.

## Trust and Validation

The release includes:

- Confidence Score Engine.
- Evidence Coverage Score.
- OpenVals Score.
- OpenVals Trust Index.
- Source lineage.
- Human approval workflow before publication.
- Public disclaimer that Trust Index measures evidence quality, not company quality.

## Verification Summary

Local verification passed:

- `ruff check app --no-cache`
- `pytest`
- `npm run lint`
- `npm run build`

GitHub Actions for PR #22 passed:

- `api`
- `web`

See `docs/RELEASE_CANDIDATE_AUDIT.md` for full evidence.

## Tagging Recommendation

Do not tag `v0.1.0-beta` yet.

Before tagging:

1. Resolve missing `/api/v1/evidence` and `/api/v1/lineage` routes or update the release checklist.
2. Rerun the release candidate audit.
3. Confirm production health behind `https://apip.openvalidations.com`.
4. Confirm beta waitlist and enterprise inquiry submissions work in production.

Once those checks pass, tag:

```bash
git tag v0.1.0-beta
git push origin v0.1.0-beta
```
