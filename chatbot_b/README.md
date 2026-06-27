# Chatbot B

REST chat backend for BillBay Intelligence. Uses the same LangGraph BI pipeline as `ai_microservice` (report resolution, VCORBI data, Claude narration).

## Prerequisites

1. **Infrastructure** — Postgres + catalog from `ai_microservice` (see repo root README).
2. **Environment** — `ai_microservice/.env` with valid `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `DATABASE_URL`, `VCORBI_URL`.
3. **VCORBI** — `vcorbi_sim` Docker or production read-only MySQL.

## Install & run

```powershell
cd chatbot_b
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Server: **http://127.0.0.1:8001**  
Docs: **http://127.0.0.1:8001/docs**

## API

### `POST /chat`

```json
{
  "user_id": "42",
  "message": "Show me monthly sales performance",
  "access_level": 50
}
```

Response:

```json
{
  "status": "ok",
  "reply": "…natural language summary and data table…"
}
```

- `user_id`: string; numeric values map to VCORBI `user_id` (e.g. `42`). Non-numeric names use demo user `42`.
- `access_level`: optional, default `50` — controls which reports are accessible.

### `GET /health`

Returns `{"status": "ok", "service": "chatbot-b"}`.

## Test

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8001/chat" `
  -ContentType "application/json" `
  -Body '{"user_id":"42","message":"Show me monthly sales performance"}'
```
