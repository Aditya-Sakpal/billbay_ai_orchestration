# billbay_ai_orchestration

Monorepo for BillBay AI services and orchestration components.

## Services

| Folder | Description |
|--------|-------------|
| [`ai_microservice/`](ai_microservice/) | LangGraph BI agent — FastAPI, catalog, VCORBI query pipeline, WebSocket chat |

Additional microservices can be added as sibling folders under this repo.

## Quick start (ai_microservice)

```bash
cd ai_microservice
cp .env.example .env
docker compose up -d
pip install -r requirements.txt
python -m app.catalog.ingest
# apply migrations, run embeddings — see ai_microservice/README.md
uvicorn app.main:app --reload --port 8000
```
