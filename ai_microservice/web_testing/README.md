# BillBay Intelligence — Chat Frontend

React + Vite SPA for the BillBay BI orchestration service. Connects to the FastAPI WebSocket at `/ws/chat` and renders structured answers with report citations, filter chips, and formatted data tables.

## Prerequisites

- Node.js 20+
- Backend running at `http://localhost:8000` (see [`../README.md`](../README.md))
- Valid `ANTHROPIC_API_KEY` in the backend `.env` for live LLM responses

## Setup

```powershell
cd r:\devfuzzion\billbay\ai_microservice\ai_microservice\web_testing
copy .env.example .env
npm install
```

## Development

Run backend and frontend in separate terminals:

```powershell
# Terminal 1 — API
cd r:\devfuzzion\billbay\ai_microservice\ai_microservice
uvicorn app.main:app --reload --port 8000

# Terminal 2 — UI
cd r:\devfuzzion\billbay\ai_microservice\ai_microservice\web_testing
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Default demo identity: **user_id=42**, **access_level=50** (change in Settings).

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | REST base URL (`/health`) |
| `VITE_WS_URL` | `ws://localhost:8000` | WebSocket base URL |

## Stack

- React 19 + TypeScript
- Vite 7
- Tailwind CSS v4 + shadcn/ui
- react-markdown + remark-gfm

## Scripts

```powershell
npm run dev      # Vite dev server (port 3000)
npm run build    # Typecheck + production build to dist/
npm run preview  # Preview production build
npm run lint     # ESLint
```

## Project structure

```
web_testing/
├── index.html
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   └── index.css
├── components/chat/
├── lib/
├── data/
└── providers/
```
