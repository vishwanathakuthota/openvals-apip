# OpenVals APIP

APIP is the OpenVals AI Profitability Intelligence Platform for measuring whether AI investments are producing real economic value.

Version 1 is prepared for launch at:

```text
https://apip.openvalidations.com
```

## V1 Platform

This repository includes the Version 1 APIP foundation:

- FastAPI backend scaffold under `services/api`
- Next.js frontend under `apps/web`
- PostgreSQL and Redis topology through Docker Compose
- Celery worker scaffold
- SQLAlchemy models and Alembic migrations
- JWT login and protected REST APIs
- Confidence Score Engine with source reliability, freshness, cross-verification, and methodology scoring
- AI Reality Index with company, industry, and country rankings
- CSV ETL and source management workflow with admin approval, metric versioning, and audit logs
- Real catalog data import foundation with source attribution, confidence scoring, and lineage tracking
- Real data beta source registry, credibility engine, evidence coverage scoring, and ingestion connectors
- Company validation framework with evidence tracking, source review, reviewer notes, and OpenVals Validation Score
- Login-protected admin portal for catalog management, source review, audit logs, and seed import
- Public API key access with Free, Pro, and Enterprise daily limit tiers
- OpenVals-branded public launch pages for methodology, about, disclaimer, and developer access
- SEO metadata, favicon, Open Graph image placeholder, loading states, error states, empty states, and responsive mobile navigation
- GitHub Actions backend CI and Docker image workflows
- Sample API payloads

## Local Development

Recommended Mac local development flow:

- Full guide: [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- Start full stack: `make dev`
- Run migrations: `make migrate`
- Load seed data: `make seed`
- Run tests: `make test`
- Stop services: `make down`

## Key URLs

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`
- Methodology: `http://localhost:3000/methodology`
- About: `http://localhost:3000/about`
- Disclaimer: `http://localhost:3000/disclaimer`
- Developer docs: `http://localhost:3000/developers`

## Launch Pages

- Landing dashboard: OpenVals APIP positioning, global profitability gauge, metric cards, confidence score, and AI Reality Index leaderboard
- Methodology: confidence scoring weights, source transparency approach, and AI Reality Index formula
- About: OpenVals mission, V1 scope, and evidence-first product principles
- Disclaimer: research-use limitations and non-advice language
- Developers: API key authentication, usage tiers, and example requests

## Source Management

- Real data guide: [docs/REAL_DATA_GUIDE.md](docs/REAL_DATA_GUIDE.md)
- Real data beta architecture: [docs/REAL_DATA_ARCHITECTURE.md](docs/REAL_DATA_ARCHITECTURE.md)
- Company validation playbook: [docs/COMPANY_VALIDATION_PLAYBOOK.md](docs/COMPANY_VALIDATION_PLAYBOOK.md)
- ETL workflow: [docs/etl-source-management.md](docs/etl-source-management.md)
- AI Reality Index: [docs/ai-reality-index.md](docs/ai-reality-index.md)
- CSV templates: [samples/companies-template.csv](samples/companies-template.csv), [samples/industries-template.csv](samples/industries-template.csv), [samples/countries-template.csv](samples/countries-template.csv), [samples/models-template.csv](samples/models-template.csv), [samples/financial-metrics-template.csv](samples/financial-metrics-template.csv)
- Admin UI: `http://localhost:3000/admin`
- Admin API: `/api/v1/admin/*`
- Deployment strategy: [docs/deployment-strategy.md](docs/deployment-strategy.md)
- Production deployment guide: [docs/deployment.md](docs/deployment.md)
