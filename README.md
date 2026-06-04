# OpenVals APIP

APIP is the AI Profitability Intelligence Platform for measuring whether AI investments are producing real economic value.

## Backend V1

This repository includes the backend V1 foundation:

- FastAPI backend scaffold under `services/api`
- Next.js frontend under `apps/web`
- PostgreSQL and Redis topology through Docker Compose
- Celery worker scaffold
- SQLAlchemy models and Alembic migrations
- JWT login and protected REST APIs
- Confidence Score Engine with source reliability, freshness, cross-verification, and methodology scoring
- CSV ETL and source management workflow with admin approval, metric versioning, and audit logs
- GitHub Actions backend CI and Docker image workflows
- Sample API payloads

## Local Development

API:

```bash
cd services/api
python -m pip install ".[dev]"
uvicorn app.main:app --reload
```

Full stack:

```bash
docker compose up --build
```

Web:

```bash
cd apps/web
npm install
npm run dev
```

## Key URLs

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health/ready`

## Source Management

- ETL workflow: [docs/etl-source-management.md](docs/etl-source-management.md)
- CSV template: [samples/financial-metrics-template.csv](samples/financial-metrics-template.csv)
- Admin UI: `http://localhost:3000/admin`
