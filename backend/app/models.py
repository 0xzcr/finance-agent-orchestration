"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class RiskTolerance(str, Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"


class Market(str, Enum):
    india = "india"
    global_market = "global"


class InvestmentRequest(BaseModel):
    """User's investment request from the frontend."""
    prompt: str = Field(
        ...,
        description="What the user wants to invest in",
        min_length=5,
        max_length=500,
        json_schema_extra={"examples": ["I want to invest in AI and tech stocks in India"]},
    )
    investment_amount: str = Field(
        default="100000",
        description="Investment amount in INR",
    )
    risk_tolerance: RiskTolerance = Field(
        default=RiskTolerance.moderate,
        description="Risk appetite: conservative, moderate, or aggressive",
    )
    market: Market = Field(
        default=Market.india,
        description="Target market: india (NSE/BSE via Zerodha) or global",
    )


class InvestmentResponse(BaseModel):
    """Response containing the investment plan."""
    success: bool
    recommendation: str = ""
    error: Optional[str] = None


class ZerodhaLoginResponse(BaseModel):
    """Zerodha login URL response."""
    login_url: str


class ZerodhaCallbackRequest(BaseModel):
    """Request token from Zerodha OAuth callback."""
    request_token: str


class ZerodhaAuthStatus(BaseModel):
    """Zerodha authentication status."""
    authenticated: bool
    user_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    cerebras_configured: bool
    zerodha_configured: bool
    alpha_vantage_configured: bool
