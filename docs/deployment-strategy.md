# APIP Deployment Strategy

Status: Version 1 launch strategy for `apip.openvalidations.com`

## Deployment Target

Primary public domain from the PRD:

```text
apip.openvalidations.com
```

Recommended subdomains:

```text
apip.openvalidations.com       Next.js web app
api.apip.openvalidations.com   FastAPI API
```

The web app includes branded launch routes for `/`, `/methodology`, `/about`, `/disclaimer`, and `/developers`.

## Environments

| Environment | Purpose | Trigger |
| --- | --- | --- |
| Local | Docker Compose development | Manual |
| Preview | Pull request review | PR opened or updated |
| Staging | Production-like validation | Merge to `main` |
| Production | Public APIP platform | Release tag or protected approval |

## Cloudflare Strategy

Use Cloudflare for:

- DNS.
- TLS with Full (Strict) origin mode.
- WAF and bot protection.
- CDN caching for Next.js static assets.
- Edge rate limits for public API abuse.
- Optional Turnstile protection for signup/admin login.
- Optional Zero Trust policy for private admin routes before launch.

Caching rules:

- Cache `_next/static/*` aggressively.
- Do not cache `/api/*` by default.
- Do not cache admin routes.
- Cache public dashboard pages only if they are explicitly designed for stale-while-revalidate behavior.

Security headers:

- `Strict-Transport-Security`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Content-Security-Policy`
- `Permissions-Policy`

## Production Runtime

V1 can launch on a container platform such as Render, Fly.io, Railway, AWS ECS/Fargate, Google Cloud Run, Azure Container Apps, or Kubernetes.

Recommended managed dependencies:

- Managed PostgreSQL.
- Managed Redis.
- Object storage for CSV imports and generated exports.
- Container registry such as GitHub Container Registry.

Runtime topology:

```text
Cloudflare
  |
  +--> web service
  |
  +--> api service
          |
          +--> managed PostgreSQL
          +--> managed Redis
          +--> worker service
          +--> object storage
```

## GitHub Actions

Target workflows:

```text
.github/workflows/ci.yml
.github/workflows/docker.yml
.github/workflows/deploy-staging.yml
.github/workflows/deploy-production.yml
```

### ci.yml

Runs on pull requests and pushes to `main`.

Required checks:

- Python lint and format check.
- Python unit tests.
- Alembic migration validation.
- TypeScript lint.
- TypeScript type check.
- Frontend unit tests.
- OpenAPI schema generation check.

### docker.yml

Builds deployment images.

Steps:

- Build API image.
- Build worker image.
- Build web image.
- Run image vulnerability scan.
- Tag images with commit SHA.
- Push images to the registry on trusted branches.

### deploy-staging.yml

Runs after merge to `main` or manual dispatch.

Steps:

- Pull the immutable image tags.
- Run database migrations.
- Deploy API.
- Deploy worker.
- Deploy web.
- Run smoke tests against staging.
- Publish deployment summary.

### deploy-production.yml

Runs on release tag or manual protected approval.

Steps:

- Confirm image SHAs from staging.
- Take or verify database backup.
- Run backward-compatible migrations.
- Deploy API and worker.
- Deploy web.
- Run production smoke tests.
- Monitor error rate, latency, and queue depth.

## Database Migration Strategy

- Use Alembic migrations.
- Use expand-and-contract changes for production.
- Avoid destructive migrations in the same release as application changes.
- Take backups before production schema changes.
- Prefer forward fixes over rollback migrations after production release.

Safe migration sequence:

1. Add nullable structures.
2. Deploy code that supports old and new structures.
3. Backfill data.
4. Enforce constraints.
5. Remove old structures in a later release.

## Secrets Strategy

Required production secrets:

- `DATABASE_URL`
- `REDIS_URL`
- `SECRET_KEY`
- `API_KEY_PEPPER`
- `APIP_PUBLIC_API_KEY`
- `APIP_API_BASE_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- Object storage credentials.
- Error reporting DSN.
- Auth provider secrets.

Rules:

- Store CI/CD secrets in GitHub Actions secrets or OIDC-backed cloud roles.
- Store runtime secrets in the hosting platform secret manager.
- Never commit `.env`.
- Rotate API key pepper and auth secrets through planned maintenance procedures.

## Release Flow

Feature branch:

1. Developer opens PR.
2. CI runs.
3. Preview deploy is created if supported.
4. Review and merge after approval.

Staging:

1. Merge to `main`.
2. Build immutable images.
3. Deploy staging.
4. Run smoke tests.

Production:

1. Create release tag or manual production dispatch.
2. Confirm staging image SHAs.
3. Apply migrations.
4. Deploy production.
5. Run smoke tests.
6. Monitor.

## Smoke Tests

Minimum smoke checks:

- `GET https://apip.openvalidations.com/` returns 200.
- `GET https://apip.openvalidations.com/methodology` returns 200.
- `GET https://apip.openvalidations.com/about` returns 200.
- `GET https://apip.openvalidations.com/disclaimer` returns 200.
- `GET https://apip.openvalidations.com/developers` returns 200.
- `GET https://apip.openvalidations.com/favicon.svg` returns 200.
- `GET https://apip.openvalidations.com/og-image.svg` returns 200.
- `GET https://api.apip.openvalidations.com/health/ready` returns `ok`.
- `GET /api/v1/scoreboard` returns public metrics.
- `POST /api/v1/roi-calculator` returns valid calculator output.
- Admin login works in staging.
- Worker can process a lightweight staging ETL job.

Frontend build checks before deployment:

- `cd apps/web && npm run lint`
- `cd apps/web && npm run typecheck`
- `cd apps/web && npm run build`

## Rollback Strategy

Application:

- Redeploy previous immutable image SHA.
- Keep at least the last 5 production image sets available.

Database:

- Prefer forward-compatible migrations.
- Restore from backup only for severe data-corruption events.

Worker:

- Version ETL payloads.
- Drain or pause queues before rolling back if job schemas changed.

## Monitoring

Initial alerts:

- API 5xx rate.
- API p95 latency.
- Public API 429 spikes.
- Celery queue depth.
- ETL job failure rate.
- PostgreSQL CPU, storage, and connection pressure.
- Redis memory pressure.

Dashboards:

- Public API usage.
- Scoreboard and dashboard latency.
- ETL throughput.
- Source approval backlog.
- Confidence distribution by metric type.

## Branch Policy

- Feature branches target `main`.
- `main` must remain deployable.
- Production deployment requires passing CI, successful image build, migration validation, and protected approval.
