# APIP Folder Structure

Status: Phase 1 documentation-only proposal

This is the target implementation layout. Phase 1 creates documentation only and does not scaffold application code.

```text
openvals-apip/
  README.md
  LICENSE
  .env.example
  .gitignore
  docker-compose.yml
  docker-compose.prod.yml
  Dockerfile.api
  Dockerfile.web
  Dockerfile.worker
  docs/
    PRD.md
    architecture.md
    database-schema.md
    api-spec.md
    folder-structure.md
    docker-strategy.md
    deployment-strategy.md
  apps/
    web/
      package.json
      next.config.ts
      src/
        app/
          page.tsx
          companies/
          industries/
          countries/
          models/
          calculator/
          admin/
        components/
          charts/
          confidence/
          dashboard/
          layout/
          ui/
        features/
          scoreboard/
          companies/
          industries/
          countries/
          models/
          roi-calculator/
          admin/
        lib/
          api-client/
          auth/
          formatting/
        styles/
        types/
      tests/
  services/
    api/
      pyproject.toml
      alembic.ini
      app/
        main.py
        core/
          config.py
          logging.py
          security.py
          rate_limits.py
        api/
          deps.py
          routes/
            health.py
            scoreboard.py
            companies.py
            industries.py
            countries.py
            models.py
            metrics.py
            confidence.py
            roi_calculator.py
            sources.py
            admin.py
        domains/
          identity/
          catalog/
          metrics/
          sources/
          confidence/
          indexes/
          calculator/
          etl/
          admin/
        db/
          session.py
          models.py
          migrations/
        workers/
          celery_app.py
          tasks.py
        tests/
  pipelines/
    filings/
    reports/
    csv_import/
    synthetic_seed/
  packages/
    shared/
      openapi/
      api-client/
      schemas/
  infra/
    cloudflare/
    github-actions/
    scripts/
  samples/
    roi-calculator-request.json
    scoreboard-response.json
    company-metrics-response.json
```

## Directory Responsibilities

### apps/web

Next.js application for public dashboards, ROI calculator, and admin portal.

Owns:

- Global AI Scoreboard UI.
- Company, industry, country, and model dashboards.
- AI Reality Index pages.
- Confidence tooltips and source detail views.
- Admin workflows for analysts and administrators.

### services/api

FastAPI backend.

Owns:

- REST API.
- Authentication and API key enforcement.
- Role-based admin authorization.
- Metric calculation and confidence scoring.
- Database models and migrations.
- ETL job orchestration.
- Audit logging.

### pipelines

Python ingestion and transformation code.

Owns:

- SEC filing ingestion.
- Annual report and investor presentation ingestion.
- Earnings-call metadata ingestion.
- CSV imports.
- Synthetic seed-data generation for 50 companies, 10 industries, 10 countries, and years 2021-2026.

### packages/shared

Generated shared artifacts only.

Recommended contents:

- OpenAPI schema snapshots.
- Generated TypeScript API client.
- Shared JSON schema examples.

Business logic remains in the backend.

### infra

Deployment and operations support.

Recommended contents:

- Cloudflare notes or future IaC.
- GitHub Actions workflow templates.
- Release scripts.
- Smoke-test scripts.

## Implementation Boundaries

- The frontend never connects directly to PostgreSQL or Redis.
- Public dashboards read through FastAPI.
- Admin actions always go through authenticated FastAPI routes.
- ETL workers write through domain services or well-defined repository modules.
- PostgreSQL migrations live in `services/api`.
- Public examples live in `samples`.

## Phase 1 Created Files

- `docs/architecture.md`
- `docs/database-schema.md`
- `docs/api-spec.md`
- `docs/folder-structure.md`
- `docs/docker-strategy.md`
- `docs/deployment-strategy.md`
