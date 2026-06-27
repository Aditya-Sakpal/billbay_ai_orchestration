# billbay_ai_orchestration

Monorepo for BillBay AI services and orchestration components.

## Services

| Folder | Description |
|--------|-------------|
| [`ai_microservice/`](ai_microservice/) | LangGraph BI agent — FastAPI, catalog, VCORBI query pipeline, WebSocket chat |
| [`ai_microservice/web_testing/`](ai_microservice/web_testing/) | React + Vite chat UI — BillBay Intelligence frontend |
| [`chatbot_b/`](chatbot_b/) | REST chat backend — LangGraph BI pipeline on `POST /chat` (port 8001) |

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
