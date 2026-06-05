COMPOSE = docker compose

.PHONY: dev migrate seed test down

dev:
	$(COMPOSE) up --build

migrate:
	$(COMPOSE) run --rm migrate

seed:
	$(COMPOSE) run --rm seed

test:
	$(COMPOSE) run --rm api pytest
	cd apps/web && npm run typecheck && npm run build

down:
	$(COMPOSE) down
