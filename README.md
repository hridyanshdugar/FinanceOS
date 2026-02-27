# FinanceOS

An AI-native workspace for wealth advisors. FinanceOS scales a single advisor's capacity from 200 to 2,000 clients by automating data analysis, financial calculations, compliance checks, and client communication drafting — while keeping the human advisor in full control of every decision.

Built for Canadian financial advisors. All client data, tax rules (CRA), contribution limits (RRSP, TFSA, FHSA, RESP), and regulatory references (CIRO) are Canadian-specific.

## What it does

When an advisor selects a client, FinanceOS displays a workspace with their full financial picture: accounts, balances, contribution room, goals, tax documents, client notes, and action items. The advisor can then "Ask Shadow" to dispatch AI agents that work in parallel:

- **Context Agent** (Claude) — reads the client's profile, goals, documents, and conversation history to generate a personalized draft email
- **Quant Agent** (GPT-4o) — writes and executes Python code for financial calculations (tax brackets, contribution optimization, CESG, HBP comparisons), then returns the results with formulas
- **Compliance Agent** (Claude) — audits the analysis against CRA rules, CIRO suitability requirements, and contribution limits, with hard-coded regulatory thresholds injected as ground truth

All three agents receive the full client context from the database. They never fabricate numbers — if data is missing, they output "UNKNOWN." Every workflow ends with the advisor reviewing and approving (or editing, or rejecting) the output.

The system also runs a proactive **Shadow Backtest** that scans all clients for opportunities: idle cash, RRSP deadline approaches, RESP CESG optimization, OAS clawback risk, and RRIF minimum withdrawals. These surface as action items on the dashboard.

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS v4, shadcn/ui, Zustand |
| Backend | FastAPI (Python), Uvicorn, SQLite3, Pydantic |
| AI | Claude Sonnet (Anthropic) for context/compliance/synthesis, GPT-4o (OpenAI) for quantitative analysis |
| Communication | WebSockets for real-time agent dispatch and status updates |

## Project structure

```
FinanceOS/
  backend/
    agents/          # Context, Quant, Compliance, Researcher agents + orchestrator
    db/              # SQLite schema, database module, seed data
    models/          # Pydantic models
    routes/          # REST API endpoints + WebSocket handler
    services/        # LLM client wrappers, shadow backtest scanner
    config.py        # Environment variable configuration
    main.py          # FastAPI application entry point
  frontend/
    app/             # Next.js App Router pages and global styles
    components/      # React components (layout, sidebar, workspace, conversation, artifact)
    hooks/           # WebSocket hook
    lib/             # Types, API client, Zustand store
```

## Local development

### Prerequisites

- Python 3.9+
- Node.js 18+
- An Anthropic API key and an OpenAI API key

### Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env with your API keys
cat > .env << 'EOF'
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
EOF

python3 -m uvicorn main:app --port 8000 --reload
```

The backend initializes the SQLite database, seeds 8 Canadian client profiles with realistic financial data, and runs an initial shadow backtest on startup.

### Frontend

```bash
cd frontend
pnpm install   # or npm install
pnpm dev       # or npm run dev
```

Open http://localhost:3000. The frontend connects to the backend at `localhost:8000` via REST and WebSocket.

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for the Quant Agent (GPT-4o) |
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Context, Compliance, and synthesis (Claude) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins. Defaults to `http://localhost:3000` |

### Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | No | Backend API URL. Defaults to `http://localhost:8000` |
| `NEXT_PUBLIC_WS_URL` | No | Backend WebSocket URL. Defaults to `ws://localhost:8000/ws` |

## Railway deployment

FinanceOS is designed as two separate services on Railway: a Python backend and a Node.js frontend.

### 1. Create a new Railway project

Go to https://railway.app/new and create a blank project.

### 2. Deploy the backend

Add a new service from your GitHub repo. Configure it:

- **Root directory**: `backend`
- **Start command**: `python start.py`

Add these environment variables in the Railway service settings:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
CORS_ORIGINS=https://your-frontend-domain.up.railway.app
```

Railway will assign a public domain (e.g., `your-backend-xxxx.up.railway.app`). Note this URL.

### 3. Deploy the frontend

Add a second service from the same repo. Configure it:

- **Root directory**: `frontend`

Railway auto-detects pnpm from the lockfile, runs `pnpm install`, `pnpm build`, and `pnpm start`. The start script binds to `0.0.0.0` on `$PORT` automatically.

Add these environment variables (must be set before the build, since Next.js inlines `NEXT_PUBLIC_*` at build time):

```
NEXT_PUBLIC_API_URL=https://your-backend-xxxx.up.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend-xxxx.up.railway.app/ws
```

Note: use `wss://` (not `ws://`) for the WebSocket URL in production since Railway terminates TLS.

### 4. Verify

Once both services are deployed, open the frontend URL. The dashboard should load with 8 seeded clients, 3 pending action items, and the full workspace. Select a client and click "Ask Shadow" to test the agent pipeline.

### Notes on Railway

- The backend's `railway.json` declares a persistent volume mounted at `/data`. The SQLite database is written there so it survives redeploys. If you need to reset the seed data, delete the volume and redeploy.
- Railway's free tier has usage limits. The LLM API calls (Claude + GPT-4o) are billed by Anthropic and OpenAI directly, not by Railway.
- If the WebSocket connection fails, check that your backend domain is correct and uses `wss://` in the frontend env var.

## Demo notes

- There is no login page. The app loads directly into the advisor workspace with a hardcoded advisor identity ("Alex").
- Client data is seeded on startup with 8 Canadian client profiles spanning different provinces, income levels, account types, and life stages.
- The agents use real LLM calls (Claude and GPT-4o). Without valid API keys, agent calls will fail gracefully with error messages.
