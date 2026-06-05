# APIP Production Deployment

Production domain:

```text
https://apip.openvalidations.com
```

This guide covers the Docker Compose, NGINX, SSL, environment, backup, and release steps for APIP Version 1.

## Runtime Topology

```text
Cloudflare
  |
  +--> VPS ports 80/443
          |
          +--> nginx
                  |
                  +--> web:3000
                  +--> api:8000
                          |
                          +--> postgres:5432
                          +--> redis:6379
                          +--> worker
```

Only NGINX publishes host ports. API, web, PostgreSQL, Redis, and worker run on private Docker networks.

## Files

| File | Purpose |
| --- | --- |
| `docker-compose.prod.yml` | Production Docker Compose topology |
| `infra/nginx/templates/default.conf.template` | SSL-ready reverse proxy config |
| `infra/nginx/certs/fullchain.pem` | TLS certificate mounted into NGINX |
| `infra/nginx/certs/privkey.pem` | TLS private key mounted into NGINX |
| `infra/nginx/acme/` | ACME challenge webroot if using Certbot |
| `infra/scripts/backup_postgres.sh` | PostgreSQL backup script |
| `.github/workflows/deploy-production.yml` | Manual production deployment workflow |

## Environment Variables

Create a production `.env` on the server. Do not commit it.

| Variable | Required | Description |
| --- | --- | --- |
| `APP_ENV` | Yes | Set to `production` to disable interactive API docs |
| `APIP_DOMAIN` | Yes | Public web domain, `apip.openvalidations.com` |
| `APIP_IMAGE_REGISTRY` | Yes | Image registry prefix, for example `ghcr.io/openvals` |
| `APIP_ENV_FILE` | No | Compose env file path, defaults to `.env` |
| `IMAGE_TAG` | Yes | Immutable image tag to run |
| `POSTGRES_USER` | Yes | PostgreSQL application user |
| `POSTGRES_PASSWORD` | Yes | Strong PostgreSQL password |
| `POSTGRES_DB` | Yes | PostgreSQL database name |
| `DATABASE_URL` | Yes | SQLAlchemy URL, for example `postgresql+psycopg://apip:...@postgres:5432/apip` |
| `REDIS_URL` | Yes | Redis URL for API cache and rate-limit state |
| `CELERY_BROKER_URL` | Yes | Redis broker URL for worker jobs |
| `CELERY_RESULT_BACKEND` | Yes | Redis result backend URL |
| `SECRET_KEY` | Yes | Strong JWT signing secret, at least 32 bytes |
| `API_KEY_PEPPER` | Yes | Secret pepper used for API key hashing |
| `WEB_PUBLIC_API_BASE_URL` | Yes | Browser-facing API origin, `https://apip.openvalidations.com` |
| `APIP_API_BASE_URL` | Yes | Server-side API origin for Next.js, `http://api:8000` in Compose |
| `APIP_PUBLIC_API_KEY` | Yes | Public API key used by the web app for server-rendered public pages |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins, including `https://apip.openvalidations.com` |

Recommended production values:

```env
APP_ENV=production
APIP_DOMAIN=apip.openvalidations.com
APIP_IMAGE_REGISTRY=ghcr.io/openvals
IMAGE_TAG=<immutable-sha>
POSTGRES_USER=apip
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=apip
DATABASE_URL=postgresql+psycopg://apip:<strong-password>@postgres:5432/apip
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
SECRET_KEY=<strong-random-secret>
API_KEY_PEPPER=<strong-random-pepper>
WEB_PUBLIC_API_BASE_URL=https://apip.openvalidations.com
APIP_API_BASE_URL=http://api:8000
APIP_PUBLIC_API_KEY=<generated-admin-api-key>
CORS_ORIGINS=https://apip.openvalidations.com
```

## VPS Checklist

- Provision a Linux VPS with at least 2 vCPU, 4 GB RAM, and enough disk for PostgreSQL growth and backups.
- Create a non-root deploy user with SSH key access.
- Install security updates.
- Enable a firewall that allows only SSH, HTTP, and HTTPS.
- Clone the APIP repository into the deployment path, for example `/opt/apip`.
- Create the production `.env` file on the server with restrictive permissions.

## Docker Checklist

- Install Docker Engine and Docker Compose plugin.
- Add the deploy user to the `docker` group.
- Authenticate to GHCR if images are private.
- Confirm production images exist for API, worker, and web with the same immutable `IMAGE_TAG`.
- Run `docker compose -f docker-compose.prod.yml config` before the first launch.
- Start with `IMAGE_TAG=<sha> docker compose -f docker-compose.prod.yml up -d`.

## Cloudflare Checklist

- Add `apip.openvalidations.com` as a proxied DNS record.
- Set SSL/TLS mode to Full (Strict) after origin certificates are installed.
- Enable WAF managed rules.
- Enable bot protection appropriate for public API access.
- Do not cache `/api/*`, `/admin/*`, or health routes.
- Cache Next.js static assets under `/_next/static/*`.

## DNS Checklist

- Point `apip.openvalidations.com` to the VPS public IP.
- Keep TTL low during first launch.
- Verify `dig apip.openvalidations.com` returns the expected record.
- Confirm Cloudflare proxy status matches the launch plan.

## SSL Checklist

NGINX expects:

```text
infra/nginx/certs/fullchain.pem
infra/nginx/certs/privkey.pem
```

Supported SSL paths:

- Cloudflare Origin Certificate copied into the two files above.
- Certbot certificate copied or symlinked into the same paths.
- ACME HTTP challenge files served from `infra/nginx/acme/`.

Start NGINX only after certificate files exist. Then verify:

```bash
curl --fail https://apip.openvalidations.com/healthz
curl --fail https://apip.openvalidations.com/api/v1/health
```

## PostgreSQL Volume Checklist

- Use the named Docker volume `apip_postgres_data`.
- Keep the volume on persistent disk.
- Do not remove the volume during container refreshes.
- Run `infra/scripts/backup_postgres.sh` before deployments and migrations.
- Periodically test restore into a disposable database.

## Redis Checklist

- Use the named Docker volume `apip_redis_data`.
- Redis append-only persistence is enabled in production compose.
- Monitor memory usage and eviction behavior.
- Use separate Redis DB indexes for API cache, Celery broker, and Celery results.

## Logs Checklist

- NGINX logs are stored in the named Docker volume `apip_nginx_logs`.
- Inspect app logs with `docker compose -f docker-compose.prod.yml logs api web worker nginx`.
- Forward logs to the VPS log pipeline or a managed logging service before public launch.
- Alert on API 5xx spikes, health degradation, worker failures, and disk pressure.

## Database Backups

Run a compressed backup:

```bash
./infra/scripts/backup_postgres.sh
```

The script writes to:

```text
./backups/postgres/apip-<database>-<timestamp>.sql.gz
```

Recommended schedule:

- Before every production deploy.
- Daily automated backup.
- Weekly off-server backup copy.
- Monthly restore drill.

## GitHub Actions Deployment

Workflow:

```text
.github/workflows/deploy-production.yml
```

Required repository or environment secrets:

| Secret | Description |
| --- | --- |
| `PRODUCTION_HOST` | VPS hostname or IP |
| `PRODUCTION_USER` | SSH deploy user |
| `PRODUCTION_SSH_KEY` | Private SSH key for the deploy user |
| `PRODUCTION_DEPLOY_PATH` | Repository path on the VPS |

Manual inputs:

| Input | Description |
| --- | --- |
| `image_tag` | Immutable image tag to deploy |
| `git_ref` | Git ref to deploy from, default `main` |

The workflow:

1. Connects to the VPS over SSH.
2. Fetches the requested ref.
3. Runs a PostgreSQL backup.
4. Pulls production images.
5. Starts Compose with `up -d --remove-orphans`.
6. Runs `https://apip.openvalidations.com/api/v1/health`.

## Launch Smoke Tests

Run these after every deploy:

```bash
curl --fail https://apip.openvalidations.com/
curl --fail https://apip.openvalidations.com/methodology
curl --fail https://apip.openvalidations.com/developers
curl --fail https://apip.openvalidations.com/api/v1/health
curl --fail https://apip.openvalidations.com/health/ready
```

Expected `/api/v1/health` response:

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
