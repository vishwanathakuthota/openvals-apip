# AI Economics Local Verification

Branch: `feature/ai-economics-intelligence`

Date: 2026-06-15

## Objective

Verify Sprint 7 locally before production deployment.

## Docker Compose

Command:

```bash
docker compose up -d --build
```

Result: Passed after resetting stale local Docker volumes.

Initial finding:

- The existing local Postgres volume had `alembic_version=20260605_0006`.
- This branch contains migration head `20260604_0001`.
- Alembic failed with `Can't locate revision identified by '20260605_0006'`.

Resolution:

```bash
docker compose down -v
docker compose up -d --build
```

Current running services:

- `postgres`: running and healthy
- `redis`: running and healthy
- `api`: running on `http://localhost:8000`
- `web`: running on `http://localhost:3000`
- `worker`: running

## Migration

Command:

```bash
docker compose run --rm migrate
```

Result: Passed.

## Seed Data

Command:

```bash
docker compose run --rm seed
```

Result: Passed.

Seed data includes:

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

## Code Verification

Commands:

```bash
cd services/api
ruff check app --no-cache
python -m pytest

cd ../../apps/web
npm run lint
npm run build
```

Results:

- `ruff check app --no-cache`: passed
- `pytest`: passed, 23 tests
- `npm run lint`: passed
- `npm run build`: passed

## Frontend Route Verification

Base URL: `http://localhost:3000`

| Route | Status |
| --- | --- |
| `/` | 200 |
| `/companies/microsoft` | 200 |
| `/companies/nvidia` | 200 |
| `/companies/alphabet` | 200 |
| `/leaderboard` | 200 |
| `/trust-center` | 200 |
| `/developers` | 200 |
| `/ai-economics` | 200 |
| `/ai-profitability` | 200 |

## API Verification

Base URL: `http://localhost:8000`

Public API routes require:

```bash
X-API-Key: apip_live_local_dev_key
```

| Route | Status |
| --- | --- |
| `/api/v1/health` | 200 |
| `/api/v1/ai-revenue` | 200 |
| `/api/v1/ai-investment` | 200 |
| `/api/v1/ai-profitability` | 200 |
| `/api/v1/ai-economics` | 200 |
| `/api/v1/companies/microsoft` | 200 |

## AI Economics Company Page Verification

Verified visible AI Economics cards on:

- `/companies/microsoft`
- `/companies/nvidia`
- `/companies/alphabet`

Each company page displays:

- AI Revenue Estimate
- AI Investment
- Infrastructure Spend
- AI Profitability Score
- Confidence score
- Source count
- Last updated

## Fixes Made During Verification

1. Company slug lookup

   The backend company detail route previously accepted only database IDs. It now accepts either ID or slug for:

   - `/api/v1/companies/{company_id_or_slug}`
   - `/api/v1/companies/{company_id_or_slug}/metrics`

2. Frontend company fallback lookup

   The frontend fallback entity lookup now matches either `id` or `slug`, preventing slug routes from falling back to the wrong company.

3. AI Economics metrics on company pages

   Company pages now fetch `/api/v1/ai-economics/reports/{company_slug}` and display the Sprint 7 economics metrics as first-class cards.

4. Route compatibility

   Added local route aliases:

   - `/leaderboard` renders the AI Profitability leaderboard.
   - `/trust-center` renders the AI Economics dashboard.

5. API test coverage

   Added a test proving `/api/v1/companies/microsoft` resolves Microsoft by slug and returns AI revenue/spend metrics.

## Production Readiness Notes

- The local Docker volume reset was only required because this workstation had a database stamped from another branch.
- A fresh production database will not hit the stale local revision issue.
- Existing production databases should be checked for Alembic revision alignment before deploying this branch.
