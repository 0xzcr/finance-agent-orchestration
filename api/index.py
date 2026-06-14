"""
Vercel Serverless Function — Main API entry point.
Handles all /api/* routes via FastAPI mounted as a serverless function.
"""

import os
import sys
import traceback
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

# ─── Environment Setup ───────────────────────────────────────────────────────

# Add finance_agents to path for tool imports
FINANCE_AGENTS_SRC = Path(__file__).parent / "finance_agents" / "src"
if FINANCE_AGENTS_SRC.exists():
    sys.path.insert(0, str(FINANCE_AGENTS_SRC))


# ─── Configuration ───────────────────────────────────────────────────────────

CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY", "")
CEREBRAS_MODEL = os.environ.get("CEREBRAS_MODEL", "llama-4-scout-17b-16e-instruct")
KITE_API_KEY = os.environ.get("KITE_API_KEY", "")
KITE_API_SECRET = os.environ.get("KITE_API_SECRET", "")
KITE_ACCESS_TOKEN = os.environ.get("KITE_ACCESS_TOKEN", "")
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")


# ─── Models ──────────────────────────────────────────────────────────────────

class RiskTolerance(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"


class Market(str, Enum):
    india = "india"
    global_market = "global"


class InvestmentRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)
    investment_amount: str = Field(default="100000")
    risk_tolerance: RiskTolerance = Field(default=RiskTolerance.moderate)
    market: Market = Field(default=Market.india)


class InvestmentResponse(BaseModel):
    success: bool
    recommendation: str = ""
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    cerebras_configured: bool
    zerodha_configured: bool
    alpha_vantage_configured: bool


class ZerodhaLoginResponse(BaseModel):
    login_url: str


class ZerodhaCallbackRequest(BaseModel):
    request_token: str


class ZerodhaAuthStatus(BaseModel):
    authenticated: bool
    user_id: Optional[str] = None


# ─── FastAPI App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Finance Agent Orchestration API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/api")
async def root():
    return {
        "service": "Finance Agent Orchestration API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        cerebras_configured=bool(CEREBRAS_API_KEY),
        zerodha_configured=bool(KITE_API_KEY),
        alpha_vantage_configured=bool(ALPHA_VANTAGE_API_KEY),
    )


@app.get("/api/zerodha/login", response_model=ZerodhaLoginResponse)
async def zerodha_login():
    if not KITE_API_KEY:
        raise HTTPException(status_code=500, detail="KITE_API_KEY not configured")
    return ZerodhaLoginResponse(
        login_url=f"https://kite.zerodha.com/connect/login?v=3&api_key={KITE_API_KEY}"
    )


@app.post("/api/zerodha/callback")
async def zerodha_callback(request: ZerodhaCallbackRequest):
    try:
        from kiteconnect import KiteConnect

        kite = KiteConnect(api_key=KITE_API_KEY)
        data = kite.generate_session(
            request_token=request.request_token,
            api_secret=KITE_API_SECRET,
        )
        return {
            "success": True,
            "access_token": data["access_token"],
            "user_id": data.get("user_id", ""),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/zerodha/status", response_model=ZerodhaAuthStatus)
async def zerodha_status():
    return ZerodhaAuthStatus(authenticated=bool(KITE_ACCESS_TOKEN))


@app.post("/api/invest", response_model=InvestmentResponse)
async def create_investment_plan(request: InvestmentRequest):
    if not CEREBRAS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Cerebras API key not configured. Set CEREBRAS_API_KEY in Vercel environment variables.",
        )

    try:
        recommendation = _run_investment_crew(
            user_prompt=request.prompt,
            investment_amount=request.investment_amount,
            risk_tolerance=request.risk_tolerance.value,
            market=request.market.value,
        )
        return InvestmentResponse(success=True, recommendation=recommendation)
    except Exception as e:
        traceback.print_exc()
        return InvestmentResponse(
            success=False,
            error=f"Failed to generate investment plan: {str(e)}",
        )


# ─── Crew Runner ─────────────────────────────────────────────────────────────

def _run_investment_crew(
    user_prompt: str,
    investment_amount: str,
    risk_tolerance: str,
    market: str,
) -> str:
    """Run the 4-agent investment crew."""
    from crewai import Agent, Crew, Process, Task

    # Configure Cerebras via LiteLLM
    os.environ["CEREBRAS_API_KEY"] = CEREBRAS_API_KEY
    os.environ["OPENAI_API_KEY"] = CEREBRAS_API_KEY
    os.environ["OPENAI_API_BASE"] = "https://api.cerebras.ai/v1"
    os.environ["ALPHA_VANTAGE_API_KEY"] = ALPHA_VANTAGE_API_KEY

    llm_model = f"cerebras/{CEREBRAS_MODEL}"

    # Get tools
    market_tools = _get_tools(market)

    # Agents
    market_researcher = Agent(
        role="Market Research Analyst",
        goal=f"Research current market conditions and find investment opportunities based on: {user_prompt}",
        backstory=(
            "You are a senior market research analyst with 15 years of experience. "
            "You track global and Indian markets, identify trends, analyze sentiment, "
            "and find high-conviction opportunities backed by data."
        ),
        tools=market_tools,
        llm=llm_model,
        verbose=True,
    )

    strategy_planner = Agent(
        role="Investment Strategy Planner",
        goal=f"Create an investment strategy for ₹{investment_amount} with {risk_tolerance} risk tolerance.",
        backstory=(
            "You are a strategic investment planner managing portfolios worth crores. "
            "You translate research into actionable plans with specific stock picks, "
            "sector allocations, entry points, and position sizing."
        ),
        tools=market_tools[:2] if len(market_tools) >= 2 else market_tools,
        llm=llm_model,
        verbose=True,
    )

    risk_analyst = Agent(
        role="Risk Assessment Analyst",
        goal=f"Evaluate the investment strategy for risks and ensure it matches a {risk_tolerance} risk profile.",
        backstory=(
            "You are a quantitative risk analyst who has navigated multiple market crashes. "
            "You analyze volatility, correlation, concentration risk, and maximum drawdown scenarios."
        ),
        tools=market_tools[:2] if len(market_tools) >= 2 else market_tools,
        llm=llm_model,
        verbose=True,
    )

    portfolio_advisor = Agent(
        role="Portfolio Investment Advisor",
        goal=f"Deliver a final actionable investment plan for ₹{investment_amount} with exact allocations.",
        backstory=(
            "You are a certified financial advisor with 20 years of experience. "
            "Your recommendations are always specific — exact tickers, allocation percentages, "
            "entry prices, target prices, and stop-losses."
        ),
        tools=market_tools[:1] if market_tools else [],
        llm=llm_model,
        verbose=True,
    )

    # Tasks
    research_task = Task(
        description=(
            f"Research: '{user_prompt}'\n"
            f"Amount: ₹{investment_amount} | Market: {'Indian (NSE/BSE)' if market == 'india' else 'Global'}\n\n"
            "Gather current market conditions, top stocks with live prices, news/trends, and fundamentals."
        ),
        expected_output="Structured research report with prices, fundamentals, news sentiment, and 4-6 stock opportunities.",
        agent=market_researcher,
    )

    strategy_task = Task(
        description=(
            f"Build investment strategy for ₹{investment_amount}, {risk_tolerance} risk, focus: {user_prompt}\n"
            "Include: thesis, sector allocation %, stock picks with entry prices, position sizing, exit criteria."
        ),
        expected_output="Strategy document with specific allocations, stock picks, and entry/exit criteria.",
        agent=strategy_planner,
    )

    risk_task = Task(
        description=(
            f"Evaluate strategy for {risk_tolerance} risk profile:\n"
            "Assess volatility, concentration, correlation, max drawdown, hedging strategies. Give GO/NO-GO."
        ),
        expected_output="Risk report with score (1-10), per-stock risk, max drawdown, hedging, and GO/NO-GO.",
        agent=risk_analyst,
    )

    recommendation_task = Task(
        description=(
            f"Final recommendation for ₹{investment_amount}:\n"
            "Include: executive summary, allocation table (ticker, %, ₹, entry, target, stop-loss), "
            "implementation timeline, monitoring checklist, risk disclaimer. Format as markdown."
        ),
        expected_output="Professional investment memo in markdown with allocation table and disclaimers.",
        agent=portfolio_advisor,
    )

    crew = Crew(
        agents=[market_researcher, strategy_planner, risk_analyst, portfolio_advisor],
        tasks=[research_task, strategy_task, risk_task, recommendation_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return result.raw


def _get_tools(market: str):
    """Get market tools based on target market."""
    if market == "india" and KITE_ACCESS_TOKEN:
        os.environ["KITE_API_KEY"] = KITE_API_KEY
        os.environ["KITE_ACCESS_TOKEN"] = KITE_ACCESS_TOKEN
        from finance_agents.tools.zerodha_tool import (
            ZerodhaQuoteTool,
            ZerodhaHoldingsTool,
            ZerodhaHistoricalTool,
        )
        return [ZerodhaQuoteTool(), ZerodhaHoldingsTool(), ZerodhaHistoricalTool()]
    else:
        from finance_agents.tools.market_data_tool import (
            StockQuoteTool,
            MarketNewsTool,
            TopMoversTool,
            CompanyOverviewTool,
        )
        return [StockQuoteTool(), MarketNewsTool(), TopMoversTool(), CompanyOverviewTool()]
