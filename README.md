# vlang

Python 3.12 FastAPI service with a LangGraph agent pipeline, local Postgres (pgvector), and read-only VCORBI MySQL access.

## Structure

```
vlang/
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

1. Copy environment variables:

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
| `LANGFUSE_HOST`       | LangFuse server URL                  |

## Agent Graph

The LangGraph pipeline runs five placeholder nodes in sequence:

1. **intent** — classify user intent
2. **resolver** — resolve entities
3. **binder** — bind query parameters
4. **executor** — execute against data sources
5. **narrator** — generate response narrative

Each node currently returns a hardcoded placeholder string.
