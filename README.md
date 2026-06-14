# Finance Agent Orchestration

An AI-powered investment planning system with a crew of 4 specialized agents, live market data via Zerodha + Alpha Vantage, ultra-fast inference via Cerebras, and a React frontend.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  React Frontend                      │
│   (User prompt, amount, risk tolerance, market)     │
└──────────────────────┬──────────────────────────────┘
                       │ POST /api/invest
┌──────────────────────▼──────────────────────────────┐
│                 FastAPI Backend                       │
│     ┌─────────────────────────────────────┐         │
│     │         CrewAI Orchestration          │         │
│     │                                       │         │
│     │  Agent 1: Market Researcher           │         │
│     │  Agent 2: Strategy Planner            │         │
│     │  Agent 3: Risk Analyst                │         │
│     │  Agent 4: Portfolio Advisor           │         │
│     └────┬───────────────────┬─────────────┘         │
│          │                   │                       │
│   ┌──────▼──────┐    ┌──────▼──────┐               │
│   │  Cerebras   │    │   Zerodha   │               │
│   │   (LLM)    │    │ (Market API) │               │
│   └─────────────┘    └─────────────┘               │
└──────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Get API Keys

| Service | Purpose | Get Key |
|---------|---------|---------|
| **Cerebras** | LLM inference (fast + free tier) | https://cloud.cerebras.ai |
| **Zerodha Kite** | Indian market data & trading | https://developers.kite.trade |
| **Alpha Vantage** | Global market data (fallback) | https://www.alphavantage.co/support/#api-key |

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # macOS/Linux
pip install -r requirements.txt

# Configure keys
cp .env.example .env
# Edit .env with your API keys

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## How It Works

1. **User submits a prompt** — "I want to invest ₹2 lakh in AI stocks with moderate risk"
2. **Market Researcher** pulls live data from Zerodha/Alpha Vantage — prices, news, top movers
3. **Strategy Planner** builds an investment thesis with specific picks and allocations
4. **Risk Analyst** stress-tests the plan, checks concentration risk, estimates max drawdown
5. **Portfolio Advisor** delivers a final memo with exact amounts, targets, and stop-losses

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Check service status & API key configuration |
| POST | `/api/invest` | Run the investment crew |
| GET | `/api/zerodha/login` | Get Zerodha OAuth login URL |
| POST | `/api/zerodha/callback` | Exchange request_token for access_token |
| GET | `/api/zerodha/status` | Check Zerodha auth status |

### POST /api/invest — Request Body

```json
{
  "prompt": "Invest in AI and semiconductor stocks in India",
  "investment_amount": "200000",
  "risk_tolerance": "moderate",
  "market": "india"
}
```

## Project Structure

```
finance-agent-orchestration/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app + routes
│   │   ├── config.py         # Environment config
│   │   ├── cerebras_llm.py   # Cerebras LLM integration
│   │   ├── zerodha_auth.py   # Zerodha OAuth flow
│   │   ├── crew_runner.py    # CrewAI execution engine
│   │   └── models.py         # Pydantic schemas
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main app component
│   │   ├── components/
│   │   │   ├── InvestmentForm.jsx
│   │   │   ├── ResultPanel.jsx
│   │   │   └── StatusBar.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
└── finance_agents/
    └── src/finance_agents/
        ├── tools/
        │   ├── market_data_tool.py   # Alpha Vantage tools
        │   └── zerodha_tool.py       # Zerodha Kite tools
        └── crews/
            └── investment_crew/      # CrewAI agent definitions
```

## Zerodha Authentication

Zerodha uses OAuth. The flow:

1. Frontend calls `GET /api/zerodha/login` → gets login URL
2. User logs in on Zerodha's site → redirected back with `request_token`
3. Frontend sends `request_token` to `POST /api/zerodha/callback`
4. Backend exchanges it for `access_token` (valid for 1 trading day)

For development, you can set `KITE_ACCESS_TOKEN` directly in `.env` after manually logging in once.

## Disclaimer

This system generates AI-powered investment analysis for **educational and informational purposes only**. It does not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.
