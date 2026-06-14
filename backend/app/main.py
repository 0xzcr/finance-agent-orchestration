"""
FastAPI backend for the Finance Agent Orchestration system.
Connects the React frontend to the CrewAI investment agents.
"""

import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import (
    HealthResponse,
    InvestmentRequest,
    InvestmentResponse,
    ZerodhaAuthStatus,
    ZerodhaCallbackRequest,
    ZerodhaLoginResponse,
)
from app.zerodha_auth import get_login_url, generate_access_token, is_authenticated


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events."""
    print("🚀 Finance Agent API starting...")
    print(f"   Cerebras: {'✓ configured' if settings.CEREBRAS_API_KEY else '✗ missing key'}")
    print(f"   Zerodha:  {'✓ configured' if settings.KITE_API_KEY else '✗ missing key'}")
    print(f"   Alpha V:  {'✓ configured' if settings.ALPHA_VANTAGE_API_KEY else '✗ missing key'}")
    yield
    print("Finance Agent API shutting down.")


app = FastAPI(
    title="Finance Agent Orchestration API",
    description="AI-powered investment planning using CrewAI + Cerebras + Zerodha",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Root ---

@app.get("/")
async def root():
    """Root endpoint — confirms the API is running."""
    return {
        "service": "Finance Agent Orchestration API",
        "status": "running",
        "docs": "/docs",
        "frontend": "http://localhost:5173",
    }


# --- Health & Status ---

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health and configuration status."""
    return HealthResponse(
        status="healthy",
        cerebras_configured=bool(settings.CEREBRAS_API_KEY),
        zerodha_configured=bool(settings.KITE_API_KEY),
        alpha_vantage_configured=bool(settings.ALPHA_VANTAGE_API_KEY),
    )


# --- Zerodha Auth ---

@app.get("/api/zerodha/login", response_model=ZerodhaLoginResponse)
async def zerodha_login():
    """Get the Zerodha login URL for OAuth authentication."""
    try:
        url = get_login_url()
        return ZerodhaLoginResponse(login_url=url)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/zerodha/callback")
async def zerodha_callback(request: ZerodhaCallbackRequest):
    """Exchange Zerodha request_token for access_token."""
    try:
        result = generate_access_token(request.request_token)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/zerodha/status", response_model=ZerodhaAuthStatus)
async def zerodha_status():
    """Check if Zerodha is authenticated."""
    return ZerodhaAuthStatus(
        authenticated=is_authenticated(),
    )


# --- Investment Crew ---

@app.post("/api/invest", response_model=InvestmentResponse)
async def create_investment_plan(request: InvestmentRequest):
    """
    Run the 4-agent investment crew to generate a personalized investment plan.

    The crew consists of:
    1. Market Researcher — gathers live market data
    2. Strategy Planner — builds investment thesis
    3. Risk Analyst — stress-tests the plan
    4. Portfolio Advisor — delivers final recommendation
    """
    if not settings.CEREBRAS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Cerebras API key not configured. Set CEREBRAS_API_KEY in .env",
        )

    try:
        from app.crew_runner import run_investment_crew

        recommendation = run_investment_crew(
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
