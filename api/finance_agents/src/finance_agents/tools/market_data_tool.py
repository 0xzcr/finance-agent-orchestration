"""
Market data tools for the investment crew.
Uses Alpha Vantage API for real-time and historical market data.
Get a free API key at: https://www.alphavantage.co/support/#api-key
"""

import os
import json
from typing import Type

import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"


def _get_api_key() -> str:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
    if not key:
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY not set. "
            "Get a free key at https://www.alphavantage.co/support/#api-key"
        )
    return key


# --- Stock Quote Tool ---

class StockQuoteInput(BaseModel):
    """Input for getting a real-time stock quote."""
    symbol: str = Field(..., description="The stock ticker symbol, e.g. AAPL, MSFT, GOOGL")


class StockQuoteTool(BaseTool):
    name: str = "stock_quote"
    description: str = (
        "Get the latest real-time price quote for a stock symbol. "
        "Returns current price, open, high, low, volume, and change percentage."
    )
    args_schema: Type[BaseModel] = StockQuoteInput

    def _run(self, symbol: str) -> str:
        api_key = _get_api_key()
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key,
        }
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
        data = response.json()

        if "Global Quote" not in data or not data["Global Quote"]:
            return f"No quote data found for symbol '{symbol}'. Check the ticker symbol."

        quote = data["Global Quote"]
        return json.dumps({
            "symbol": quote.get("01. symbol", symbol),
            "price": quote.get("05. price", "N/A"),
            "open": quote.get("02. open", "N/A"),
            "high": quote.get("03. high", "N/A"),
            "low": quote.get("04. low", "N/A"),
            "volume": quote.get("06. volume", "N/A"),
            "previous_close": quote.get("08. previous close", "N/A"),
            "change": quote.get("09. change", "N/A"),
            "change_percent": quote.get("10. change percent", "N/A"),
        }, indent=2)


# --- Market News & Sentiment Tool ---

class MarketNewsInput(BaseModel):
    """Input for getting market news and sentiment."""
    tickers: str = Field(
        default="",
        description="Comma-separated stock tickers to filter news for, e.g. 'AAPL,MSFT'. Leave empty for general market news.",
    )
    topics: str = Field(
        default="",
        description="Comma-separated topics to filter news. Options: blockchain, earnings, ipo, mergers_and_acquisitions, financial_markets, economy_fiscal, economy_monetary, economy_macro, energy_transportation, finance, life_sciences, manufacturing, real_estate, retail_wholesale, technology",
    )


class MarketNewsTool(BaseTool):
    name: str = "market_news_sentiment"
    description: str = (
        "Get the latest market news articles with sentiment analysis. "
        "Can filter by stock tickers or topics like technology, earnings, economy_macro, etc. "
        "Returns headlines, summaries, sentiment scores, and source information."
    )
    args_schema: Type[BaseModel] = MarketNewsInput

    def _run(self, tickers: str = "", topics: str = "") -> str:
        api_key = _get_api_key()
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": api_key,
            "limit": "10",
        }
        if tickers:
            params["tickers"] = tickers
        if topics:
            params["topics"] = topics

        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
        data = response.json()

        if "feed" not in data:
            return f"No news data available. Response: {json.dumps(data)}"

        articles = []
        for article in data["feed"][:10]:
            articles.append({
                "title": article.get("title", ""),
                "summary": article.get("summary", "")[:200],
                "source": article.get("source", ""),
                "published": article.get("time_published", ""),
                "overall_sentiment": article.get("overall_sentiment_label", ""),
                "sentiment_score": article.get("overall_sentiment_score", ""),
                "tickers_mentioned": [
                    t.get("ticker", "") for t in article.get("ticker_sentiment", [])[:5]
                ],
            })

        return json.dumps(articles, indent=2)


# --- Top Gainers/Losers Tool ---

class TopMoversInput(BaseModel):
    """Input for getting top market movers."""
    pass  # No input needed


class TopMoversTool(BaseTool):
    name: str = "top_gainers_losers"
    description: str = (
        "Get today's top gaining stocks, top losing stocks, and most actively traded stocks. "
        "Useful for identifying market momentum and trending stocks."
    )
    args_schema: Type[BaseModel] = TopMoversInput

    def _run(self) -> str:
        api_key = _get_api_key()
        params = {
            "function": "TOP_GAINERS_LOSERS",
            "apikey": api_key,
        }
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
        data = response.json()

        result = {}

        if "top_gainers" in data:
            result["top_gainers"] = [
                {
                    "ticker": s.get("ticker", ""),
                    "price": s.get("price", ""),
                    "change_percent": s.get("change_percentage", ""),
                    "volume": s.get("volume", ""),
                }
                for s in data["top_gainers"][:5]
            ]

        if "top_losers" in data:
            result["top_losers"] = [
                {
                    "ticker": s.get("ticker", ""),
                    "price": s.get("price", ""),
                    "change_percent": s.get("change_percentage", ""),
                    "volume": s.get("volume", ""),
                }
                for s in data["top_losers"][:5]
            ]

        if "most_actively_traded" in data:
            result["most_active"] = [
                {
                    "ticker": s.get("ticker", ""),
                    "price": s.get("price", ""),
                    "change_percent": s.get("change_percentage", ""),
                    "volume": s.get("volume", ""),
                }
                for s in data["most_actively_traded"][:5]
            ]

        if not result:
            return f"No market mover data available. Response: {json.dumps(data)}"

        return json.dumps(result, indent=2)


# --- Company Overview Tool ---

class CompanyOverviewInput(BaseModel):
    """Input for getting company fundamental data."""
    symbol: str = Field(..., description="The stock ticker symbol, e.g. AAPL, MSFT, GOOGL")


class CompanyOverviewTool(BaseTool):
    name: str = "company_overview"
    description: str = (
        "Get fundamental company data including market cap, P/E ratio, EPS, "
        "dividend yield, 52-week high/low, sector, and business description. "
        "Essential for fundamental analysis."
    )
    args_schema: Type[BaseModel] = CompanyOverviewInput

    def _run(self, symbol: str) -> str:
        api_key = _get_api_key()
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": api_key,
        }
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
        data = response.json()

        if not data or "Symbol" not in data:
            return f"No company data found for '{symbol}'."

        return json.dumps({
            "symbol": data.get("Symbol", ""),
            "name": data.get("Name", ""),
            "description": data.get("Description", "")[:300],
            "sector": data.get("Sector", ""),
            "industry": data.get("Industry", ""),
            "market_cap": data.get("MarketCapitalization", ""),
            "pe_ratio": data.get("PERatio", ""),
            "eps": data.get("EPS", ""),
            "dividend_yield": data.get("DividendYield", ""),
            "52_week_high": data.get("52WeekHigh", ""),
            "52_week_low": data.get("52WeekLow", ""),
            "50_day_moving_avg": data.get("50DayMovingAverage", ""),
            "200_day_moving_avg": data.get("200DayMovingAverage", ""),
            "profit_margin": data.get("ProfitMargin", ""),
            "revenue_ttm": data.get("RevenueTTM", ""),
            "beta": data.get("Beta", ""),
        }, indent=2)
