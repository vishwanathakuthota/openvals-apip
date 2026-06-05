# Operational Scripts

## PostgreSQL Backup

Run a compressed production backup from the repository root:

```bash
./infra/scripts/backup_postgres.sh
```

Supported environment overrides:

| Variable | Default | Purpose |
| --- | --- | --- |
| `COMPOSE_FILE` | `docker-compose.prod.yml` | Compose file containing the `postgres` service |
| `ENV_FILE` | `.env` | Environment file with `POSTGRES_USER` and `POSTGRES_DB` |
| `BACKUP_DIR` | `./backups/postgres` | Destination directory for compressed dumps |

The script prints the created `.sql.gz` path on success.
