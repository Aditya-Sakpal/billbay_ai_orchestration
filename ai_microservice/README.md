# ai_microservice

Python 3.12 FastAPI service with a LangGraph agent pipeline, local Postgres (pgvector), and read-only VCORBI MySQL access.

## Structure

```
ai_microservice/
  app/
    main.py              # FastAPI entry point
    config.py            # pydantic-settings configuration
    database.py          # Async SQLAlchemy (local Postgres)
    vcorbi.py            # Sync SQLAlchemy (VCORBI MySQL, read-only)
    routers/             # HTTP and WebSocket routes
    agent/               # LangGraph supervisor graph (5 placeholder nodes)
    catalog/             # Report catalog loader
    session/             # Session state CRUD
  docker-compose.yml     # Postgres 16 + pgvector + LangFuse
  requirements.txt
  .env.example
```

## Prerequisites

- Python 3.12
- Docker and Docker Compose (for local Postgres and LangFuse)

## Setup

1. Copy environment variables (from this directory):

   ```bash
   cp .env.example .env
   ```

2. Start infrastructure:

   ```bash
   docker compose up -d
   ```

3. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Run the API:

   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Endpoints

| Method    | Path       | Description              |
|-----------|------------|--------------------------|
| GET       | `/health`  | Health check             |
| WebSocket | `/ws/chat` | Chat via agent graph     |

## Configuration

All settings are loaded from `.env` via `pydantic-settings`:

| Variable              | Description                          |
|-----------------------|--------------------------------------|
| `DATABASE_URL`        | Async Postgres connection string     |
| `VCORBI_URL`          | Sync MySQL connection string         |
| `ANTHROPIC_API_KEY`   | Anthropic API key                    |
| `LANGFUSE_SECRET_KEY` | LangFuse secret key                  |
| `LANGFUSE_PUBLIC_KEY` | LangFuse public key                  |
| `VCORBI_MODE`         | `mock` or `real` for local MySQL demo |
| `DATA_SOURCE_MODE`    | `vcorbi_mock` (default) or `dashboard_api` (live site) |
| `DASHBOARD_SESSION_COOKIE` | Session cookie from DevTools cURL (required for `dashboard_api`) |
| `DASHBOARD_BASE_URL`  | e.g. `https://csportal.billbay.co`   |
| `DASHBOARD_API_URL`   | API path or full URL (optional if set per report in JSON) |

## Live dashboard data (Option A)

Node 4 can call the Cornerstone BI dashboard API instead of local MySQL:

1. Log in at [csportal.billbay.co](https://csportal.billbay.co/dashboard.php).
2. Open DevTools → Network → filter **Fetch/XHR**.
3. Load a report (e.g. Sales Performance), right-click the request → **Copy as cURL**.
4. Parse it:

   ```bash
   python -m scripts.parse_curl --curl-file captured.curl --table bbz_sales_perf
   ```

5. Apply the printed `.env` values and merge the JSON into `data/dashboard_api_endpoints.json`.
6. Set `DATA_SOURCE_MODE=dashboard_api` in `.env` and restart uvicorn.
7. Verify:

   ```bash
   python -m scripts.test_dashboard_api --table bbz_sales_perf
   ```

Report metadata still comes from the Postgres catalog (ingested from CSV once). Only the **data rows** are fetched from the live API.

## Agent Graph

The LangGraph pipeline runs five placeholder nodes in sequence:

1. **intent** — classify user intent
2. **resolver** — resolve entities
3. **binder** — bind query parameters
4. **executor** — execute against data sources
5. **narrator** — generate response narrative

Each node currently returns a hardcoded placeholder string.
