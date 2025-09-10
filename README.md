# Xweather ETL with Apache Airflow (Docker)

A minimal, production-like Airflow stack (CeleryExecutor) to extract Xweather tropical cyclone data, transform to CSV, and load into PostgreSQL. Includes DAG `xweather_etl` orchestrating extract → transform → load.

## Prerequisites

- Docker Desktop 4.x+
- Git

## Project Structure

```
.
├─ dags/
│  ├─ xweather_etl.py          # Airflow DAG
│  └─ src/
│     ├─ extract_xweather.py   # Extract JSON from Xweather API
│     ├─ cleaning.py           # Transform JSON → CSV (storm.csv, track.csv)
│     └─ load.py               # Load CSV → Postgres
├─ logs/                       # Airflow logs (mounted)
├─ config/                     # Airflow config (mounted)
├─ plugins/                    # Airflow plugins (mounted)
└─ docker-compose.yaml         # Airflow stack + Redis + Postgres
```

## Quickstart

1. Clone and go to the project folder:

```bash
git clone <your_repo_url> Xweather
cd Xweather
```

2. Create `.env` for Xweather credentials (place it in `dags/.env`):

```dotenv
client_id=YOUR_XWEATHER_CLIENT_ID
client_secret=YOUR_XWEATHER_CLIENT_SECRET
# Optional overrides for Postgres inside Airflow tasks
# PG_HOST=postgres
# PG_PORT=5432
# PG_DB=airflow
# PG_USER=airflow
# PG_PASSWORD=airflow
```

3. Start the stack:

```bash
docker compose up -d
```

- First time startup may take a few minutes.
- Airflow Web UI (via API server): http://localhost:8080
  - Default user: `airflow` / `airflow` (created by the compose file)

4. Trigger the ETL DAG:

```bash
docker compose exec airflow-apiserver airflow dags trigger xweather_etl
```

5. Check task logs

- Via UI: DAGs → `xweather_etl` → Graph → task → Log
- Or from host (logs are mounted): `./logs/dag_id=xweather_etl/...`

## Data Flow

- Extract: calls Xweather API using `client_id`/`client_secret` from `dags/.env`, saves JSON under `dags/src/data/raw/`
- Transform: parses JSON into two CSVs under `dags/src/data/processed/`: `storm.csv`, `track.csv`
- Load: creates tables (if missing) and loads into Postgres service `postgres`
  - `storm(storm_id PRIMARY KEY, ...)`
  - `track(..., storm_id REFERENCES storm(storm_id) ON DELETE CASCADE)`

## Postgres Access

- Inside container:

```bash
docker compose exec postgres psql -U airflow -d airflow -c "\\dt"
```

- Optional (Desktop pgAdmin/DBeaver): expose a host port by adding to `docker-compose.yaml` → service `postgres`:

```yaml
ports:
  - "55432:5432"
```

Then connect with:

- Host: 127.0.0.1
- Port: 55432
- DB: airflow
- User/Pass: airflow / airflow

## Airflow Version Notes

- Airflow 3 uses `schedule` (not `schedule_interval`). The DAG already uses `schedule: "0 0 * * *"`.

## Troubleshooting

- Missing Python deps (e.g., `pandas`, `psycopg2-binary`): set `_PIP_ADDITIONAL_REQUIREMENTS` in `docker-compose.yaml` env for Airflow services.
- `.env` not loaded: ensure the file is at `dags/.env` (mounted into `/opt/airflow/dags/.env`).
- FK constraint errors on load: the loader truncates `track, storm` together to satisfy FK.
- Inspect recent logs quickly:

```bash
docker compose exec airflow-apiserver airflow dags list-runs -d xweather_etl | cat
```

## Git: How to Push

First time:

```bash
git init
git branch -M main
git remote add origin <your_repo_url>

git add .
git commit -m "Initial Airflow ETL: extract/transform/load with Docker"

git push -u origin main
```

Later updates:

```bash
git add -A
git commit -m "Update ETL DAG and loader"
git push
```

## License

Apache-2.0 (see Docker stack references). Adapt as needed for your project.
