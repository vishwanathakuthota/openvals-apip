# APIP Docker Strategy

Status: Phase 1 documentation-only strategy

## Goals

- Run the full APIP stack locally with Docker Compose.
- Build production-grade images for FastAPI, Next.js, and Celery workers.
- Keep PostgreSQL and Redis private in production.
- Support Cloudflare-fronted deployments.
- Keep image builds compatible with GitHub Actions.

## Target Services

```text
web       Next.js public dashboards and admin portal
api       FastAPI REST API
worker    Celery worker for ETL and recalculation jobs
postgres  Local PostgreSQL
redis     Local Redis broker/cache/rate limit store
```

Optional later services:

- `minio` for local object storage.
- `mailhog` for local email testing.
- `otel-collector` for local traces.

## Development Compose

Target file: `docker-compose.yml`

Recommended behavior:

- Bind mount application source for fast iteration.
- Use named volumes for PostgreSQL and Redis.
- Expose web on `localhost:3000`.
- Expose API on `localhost:8000`.
- Keep PostgreSQL and Redis on the internal Docker network unless direct local debugging is needed.
- Run migrations explicitly through a one-off API command.
- Include health checks for all stateful services.

Expected local ports:

| Service | Port |
| --- | --- |
| Next.js web | 3000 |
| FastAPI API | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |

## Production Compose

Target file: `docker-compose.prod.yml`

Recommended for:

- Small self-hosted deployments.
- Preview deployments.
- Deployment packaging tests.

Production Compose should:

- Use immutable image tags.
- Avoid bind mounts for application code.
- Run application containers as non-root users.
- Keep PostgreSQL and Redis unexposed publicly.
- Inject secrets at runtime.
- Support separate scaling of `api` and `worker`.
- Set restart policies for long-running services.

Managed production environments can use Compose as a topology reference while replacing local PostgreSQL and Redis with managed services.

## API Image

Target file: `Dockerfile.api`

Requirements:

- Python slim base image.
- Dependency lockfile.
- Non-root runtime user.
- No secrets baked into the image.
- Healthcheck using `/health/ready`.
- Production server command using Gunicorn with Uvicorn workers or tuned Uvicorn process management.

Target runtime command:

```text
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Worker Image

Target file: `Dockerfile.worker`

Requirements:

- Reuse API dependencies and domain modules.
- Start Celery worker process.
- Configure concurrency through environment variables.
- Emit structured logs.
- Fail fast if Redis or required settings are unavailable.

Target runtime command:

```text
celery -A app.workers.celery_app worker --loglevel=info
```

## Web Image

Target file: `Dockerfile.web`

Requirements:

- Multi-stage Node.js build.
- Lockfile-based installs.
- Next.js production build.
- Standalone output where possible.
- Non-root runtime user.
- Runtime-configurable API base URL.

Cloudflare compatibility:

- Static assets should be cacheable by hashed filename.
- Authenticated dashboard data should not be cached at the edge.
- App must not rely on local filesystem writes at runtime.

## Environment Variables

Minimum local variables:

```text
APP_ENV=development
WEB_PUBLIC_API_BASE_URL=http://localhost:8000
DATABASE_URL=postgresql+psycopg://apip:apip@postgres:5432/apip
REDIS_URL=redis://redis:6379/0
SECRET_KEY=replace-me
API_KEY_PEPPER=replace-me
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

Production variables should be provided by the deployment platform or secret manager.

## Data Volumes

Local named volumes:

- `apip_postgres_data`
- `apip_redis_data`

Production:

- Prefer managed PostgreSQL backups over raw Docker volume backups.
- Use managed Redis where possible.
- Store CSV imports and exports in object storage rather than container disks.

## Health Checks

API:

- `GET /health/live`
- `GET /health/ready`

Web:

- `GET /`

PostgreSQL:

- `pg_isready`

Redis:

- `redis-cli ping`

Worker:

- Celery inspect ping or a lightweight queue heartbeat.

## Image Tags

Recommended:

- `ghcr.io/openvals/apip-api:<git-sha>`
- `ghcr.io/openvals/apip-web:<git-sha>`
- `ghcr.io/openvals/apip-worker:<git-sha>`

Moving tags such as `staging` and `production` are acceptable only when paired with immutable SHA tags in deployment records.

## Target Developer Commands

```bash
docker compose up --build
docker compose run --rm api alembic upgrade head
docker compose run --rm api pytest
docker compose run --rm web npm test
docker compose run --rm worker celery -A app.workers.celery_app inspect ping
docker compose down
```

## Security Requirements

- Run app containers as non-root users.
- Keep base images patched.
- Scan images in GitHub Actions.
- Do not commit `.env`.
- Use read-only root filesystems where practical.
- Restrict CORS to known frontend domains in production.
