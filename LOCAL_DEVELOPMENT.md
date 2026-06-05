# APIP Local Development on Mac

This guide starts APIP locally with Docker Compose on macOS.

## Requirements

- Docker Desktop for Mac
- Git
- Make
- Optional for non-Docker frontend work: Node.js 22
- Optional for non-Docker API work: Python 3.12

## Local URLs

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:3000` |
| Backend | `http://localhost:8000` |
| Swagger | `http://localhost:8000/docs` |
| API health | `http://localhost:8000/api/v1/health` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

## One-Command Startup

From the repository root:

```bash
make dev
```

This runs:

1. PostgreSQL
2. Redis
3. Alembic migrations
4. Seed data import
5. FastAPI backend on `http://localhost:8000`
6. Next.js frontend on `http://localhost:3000`
7. Celery worker

Keep this terminal open while using APIP.

## Verify in the Browser

Open these URLs:

```text
http://localhost:3000
http://localhost:8000/docs
http://localhost:8000/api/v1/health
```

Expected health response:

```json
{
  "status": "ok",
  "checks": {
    "api": "ok",
    "postgres": "ok",
    "redis": "ok"
  }
}
```

## Verify from Terminal

```bash
curl --fail http://localhost:3000
curl --fail http://localhost:8000/docs
curl --fail http://localhost:8000/api/v1/health
```

## Make Commands

```bash
make dev
```

Builds and starts the full local stack.

```bash
make migrate
```

Runs Alembic migrations against the local PostgreSQL container.

```bash
make seed
```

Loads idempotent APIP seed data, including:

- Admin user: `admin@openvalidations.com`
- Admin password: `apip-admin-change-me`
- Local public API key: `apip_live_local_dev_key`

```bash
make test
```

Runs backend tests in Docker and frontend type/build checks locally.

```bash
make down
```

Stops the Docker Compose stack.

## Reset Local Data

Use this only when you want to delete local PostgreSQL and Redis data:

```bash
docker compose down -v
make dev
```

## Environment Files

Root Docker Compose uses:

```text
.env.example
```

Standalone service examples are available at:

```text
services/api/.env.example
apps/web/.env.example
```

For Docker Compose local development, the important values are:

```env
WEB_PUBLIC_API_BASE_URL=http://localhost:8000
APIP_API_BASE_URL=http://localhost:8000
APIP_PUBLIC_API_KEY=apip_live_local_dev_key
DATABASE_URL=postgresql+psycopg://apip:apip@postgres:5432/apip
REDIS_URL=redis://redis:6379/0
CORS_ORIGINS=http://localhost:3000
```

## Troubleshooting

If ports are already in use:

```bash
lsof -i :3000
lsof -i :8000
lsof -i :5432
lsof -i :6379
```

Then stop the conflicting local process or change the port mapping in `docker-compose.yml`.

If the frontend loads but shows fallback data, confirm the seed completed and the local API key exists:

```bash
docker compose logs seed
curl --fail -H "X-API-Key: apip_live_local_dev_key" http://localhost:8000/api/v1/companies
```

If migrations fail, inspect:

```bash
docker compose logs postgres
docker compose logs migrate
```
