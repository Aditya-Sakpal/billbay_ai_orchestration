# BillBay Intelligence — Chat Frontend

Next.js chat UI for the BillBay BI orchestration service. Connects to the FastAPI WebSocket at `/ws/chat` and renders structured answers with report citations, filter chips, and markdown data tables.

## Prerequisites

- Node.js 20+
- Backend running at `http://localhost:8000` (see [`../ai_microservice/README.md`](../ai_microservice/README.md))
- Valid `ANTHROPIC_API_KEY` in the backend `.env` for live LLM responses

## Setup

```powershell
cd r:\devfuzzion\billbay\ai_microservice\web
copy .env.example .env.local
npm install
```

## Development

Run backend and frontend in separate terminals:

```powershell
# Terminal 1 — API
cd r:\devfuzzion\billbay\ai_microservice\ai_microservice
uvicorn app.main:app --reload --port 8000

# Terminal 2 — UI
cd r:\devfuzzion\billbay\ai_microservice\web
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Default demo identity: **user_id=42**, **access_level=50** (change in Settings).

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | REST base URL (`/health`) |
| `NEXT_PUBLIC_WS_URL` | `ws://localhost:8000` | WebSocket base URL |

## WebSocket contract

- **Connect:** `ws://localhost:8000/ws/chat?user_id=42&access_level=50`
- **Send:** plain text message per turn
- **Receive:** `{ answer, report, filters, session_id, error? }`

## Features

- Branded BillBay Intelligence layout with sidebar report catalog
- Suggested prompts from golden evaluation queries
- Structured assistant cards (summary + source table)
- Dev settings panel (user ID, access level, API URLs)
- Connection status, reconnect, and backend health check
- Press `/` to focus the chat input

## Scripts

```powershell
npm run dev      # development server
npm run build    # production build
npm run start    # serve production build
npm run lint     # ESLint
```

## Verification

With the backend running, try these prompts:

1. `Show me sales for Aelina Senitro` — expect Monthly Sales Performance report + filter chips
2. `Which customers have overdue accounts?` — expect Overdue Accounts report
3. Follow-up: `What about Karen Ku?` — filters should carry context on same WebSocket session

## Project structure

```
web/
├── app/                 # Next.js App Router
├── components/chat/     # Chat UI components
├── data/                # Static report catalog & prompts
├── lib/                 # Types, parsing, storage
└── providers/           # ChatProvider + WebSocket state
```
