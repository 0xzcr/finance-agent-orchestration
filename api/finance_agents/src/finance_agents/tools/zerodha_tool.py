"""
Zerodha Kite Connect tools for the investment crew.
Provides market data and portfolio info from Zerodha's trading platform.

Setup:
1. Get API key from https://developers.kite.trade/
2. Set KITE_API_KEY and KITE_ACCESS_TOKEN in .env
"""

import os
import json
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


def _get_kite_client():
    """Initialize and return the Kite Connect client."""
    try:
        from kiteconnect import KiteConnect
    except ImportError:
        raise ImportError(
            "kiteconnect not installed. Run: pip install kiteconnect"
        )

    api_key = os.environ.get("KITE_API_KEY", "")
    access_token = os.environ.get("KITE_ACCESS_TOKEN", "")

    if not api_key:
        raise ValueError("KITE_API_KEY not set in environment.")
    if not access_token:
        raise ValueError(
            "KITE_ACCESS_TOKEN not set. Complete the login flow first."
        )

    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite


# --- Zerodha Stock Quote Tool ---

class ZerodhaQuoteInput(BaseModel):
    """Input for getting stock quote from Zerodha."""
    symbols: str = Field(
        ...,
        description="Comma-separated trading symbols in exchange:symbol format, e.g. 'NSE:RELIANCE,NSE:TCS,NSE:INFY'",
    )


class ZerodhaQuoteTool(BaseTool):
    name: str = "zerodha_stock_quote"
    description: str = (
        "Get real-time stock quotes from Zerodha for Indian stocks (NSE/BSE). "
        "Provides last price, OHLC, volume, and change percentage. "
        "Use exchange:symbol format like NSE:RELIANCE, NSE:TCS, BSE:INFY."
    )
    args_schema: Type[BaseModel] = ZerodhaQuoteInput

    def _run(self, symbols: str) -> str:
        kite = _get_kite_client()
        symbol_list = [s.strip() for s in symbols.split(",")]

        try:
            quotes = kite.quote(symbol_list)
        except Exception as e:
            return f"Error fetching quotes: {e}"

        result = {}
        for sym, data in quotes.items():
            ohlc = data.get("ohlc", {})
            result[sym] = {
                "last_price": data.get("last_price"),
                "open": ohlc.get("open"),
                "high": ohlc.get("high"),
                "low": ohlc.get("low"),
                "close": ohlc.get("close"),
                "volume": data.get("volume"),
                "change": data.get("net_change"),
                "change_percent": round(
                    ((data.get("last_price", 0) - ohlc.get("close", 1)) / ohlc.get("close", 1)) * 100, 2
                ) if ohlc.get("close") else None,
                "buy_quantity": data.get("buy_quantity"),
                "sell_quantity": data.get("sell_quantity"),
            }

        return json.dumps(result, indent=2)


# --- Zerodha Holdings Tool ---

class ZerodhaHoldingsInput(BaseModel):
    """Input for getting portfolio holdings."""
    pass


class ZerodhaHoldingsTool(BaseTool):
    name: str = "zerodha_holdings"
    description: str = (
        "Get the current portfolio holdings from your Zerodha account. "
        "Shows all stocks you currently own with quantity, average price, "
        "current value, and P&L."
    )
    args_schema: Type[BaseModel] = ZerodhaHoldingsInput

    def _run(self) -> str:
        kite = _get_kite_client()

        try:
            holdings = kite.holdings()
        except Exception as e:
            return f"Error fetching holdings: {e}"

        if not holdings:
            return "No holdings found in the portfolio."

        result = []
        total_investment = 0
        total_current = 0

        for h in holdings:
            investment = h.get("quantity", 0) * h.get("average_price", 0)
            current_val = h.get("quantity", 0) * h.get("last_price", 0)
            pnl = current_val - investment
            total_investment += investment
            total_current += current_val

            result.append({
                "symbol": h.get("tradingsymbol"),
                "exchange": h.get("exchange"),
                "quantity": h.get("quantity"),
                "average_price": h.get("average_price"),
                "last_price": h.get("last_price"),
                "investment": round(investment, 2),
                "current_value": round(current_val, 2),
                "pnl": round(pnl, 2),
                "pnl_percent": round((pnl / investment) * 100, 2) if investment else 0,
            })

        summary = {
            "total_investment": round(total_investment, 2),
            "total_current_value": round(total_current, 2),
            "total_pnl": round(total_current - total_investment, 2),
            "total_pnl_percent": round(
                ((total_current - total_investment) / total_investment) * 100, 2
            ) if total_investment else 0,
            "holdings_count": len(result),
            "holdings": result,
        }

        return json.dumps(summary, indent=2)


# --- Zerodha Historical Data Tool ---

class ZerodhaHistoricalInput(BaseModel):
    """Input for getting historical price data."""
    symbol: str = Field(
        ..., description="Trading symbol in exchange:symbol format, e.g. 'NSE:RELIANCE'"
    )
    interval: str = Field(
        default="day",
        description="Candle interval: minute, 3minute, 5minute, 10minute, 15minute, 30minute, 60minute, day, week, month",
    )
    days: int = Field(
        default=30,
        description="Number of days of historical data to fetch (max 365 for daily)",
    )


class ZerodhaHistoricalTool(BaseTool):
    name: str = "zerodha_historical_data"
    description: str = (
        "Get historical OHLCV (Open, High, Low, Close, Volume) candle data "
        "for an Indian stock from Zerodha. Useful for trend analysis and "
        "calculating moving averages. Returns data for the specified number of days."
    )
    args_schema: Type[BaseModel] = ZerodhaHistoricalInput

    def _run(self, symbol: str, interval: str = "day", days: int = 30) -> str:
        from datetime import datetime, timedelta

        kite = _get_kite_client()

        # Resolve instrument token
        exchange, tradingsymbol = symbol.split(":") if ":" in symbol else ("NSE", symbol)

        try:
            instruments = kite.instruments(exchange)
            instrument = next(
                (i for i in instruments if i["tradingsymbol"] == tradingsymbol), None
            )
            if not instrument:
                return f"Instrument '{symbol}' not found on {exchange}."

            instrument_token = instrument["instrument_token"]

            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)

            data = kite.historical_data(
                instrument_token,
                from_date.strftime("%Y-%m-%d"),
                to_date.strftime("%Y-%m-%d"),
                interval,
            )
        except Exception as e:
            return f"Error fetching historical data: {e}"

        if not data:
            return f"No historical data found for {symbol}."

        # Summarize — return last N candles
        candles = []
        for d in data[-20:]:  # Last 20 candles
            candles.append({
                "date": d["date"].strftime("%Y-%m-%d") if hasattr(d["date"], "strftime") else str(d["date"]),
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"],
            })

        # Basic stats
        closes = [d["close"] for d in data]
        result = {
            "symbol": symbol,
            "interval": interval,
            "period_days": days,
            "total_candles": len(data),
            "latest_close": closes[-1] if closes else None,
            "period_high": max(d["high"] for d in data),
            "period_low": min(d["low"] for d in data),
            "avg_close": round(sum(closes) / len(closes), 2) if closes else None,
            "recent_candles": candles,
        }

        return json.dumps(result, indent=2, default=str)


# --- Zerodha Place Order Tool ---

class ZerodhaOrderInput(BaseModel):
    """Input for placing an order on Zerodha."""
    symbol: str = Field(..., description="Trading symbol, e.g. 'RELIANCE'")
    exchange: str = Field(default="NSE", description="Exchange: NSE or BSE")
    transaction_type: str = Field(..., description="BUY or SELL")
    quantity: int = Field(..., description="Number of shares to buy/sell")
    order_type: str = Field(
        default="MARKET",
        description="Order type: MARKET, LIMIT, SL, SL-M",
    )
    price: float = Field(
        default=0, description="Price for LIMIT orders (0 for MARKET orders)"
    )
    product: str = Field(
        default="CNC",
        description="Product type: CNC (delivery), MIS (intraday), NRML (F&O)",
    )


class ZerodhaOrderTool(BaseTool):
    name: str = "zerodha_place_order"
    description: str = (
        "Place a buy or sell order on Zerodha. Supports MARKET and LIMIT orders. "
        "Use CNC for delivery (long-term), MIS for intraday. "
        "IMPORTANT: This executes real trades. Use with caution."
    )
    args_schema: Type[BaseModel] = ZerodhaOrderInput

    def _run(
        self,
        symbol: str,
        exchange: str = "NSE",
        transaction_type: str = "BUY",
        quantity: int = 1,
        order_type: str = "MARKET",
        price: float = 0,
        product: str = "CNC",
    ) -> str:
        kite = _get_kite_client()

        try:
            order_params = {
                "tradingsymbol": symbol,
                "exchange": exchange,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "order_type": order_type,
                "product": product,
                "variety": "regular",
            }

            if order_type == "LIMIT" and price > 0:
                order_params["price"] = price

            order_id = kite.place_order(**order_params)

            return json.dumps({
                "status": "success",
                "order_id": order_id,
                "message": f"{transaction_type} order placed for {quantity} shares of {exchange}:{symbol}",
                "details": order_params,
            }, indent=2)

        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": str(e),
            }, indent=2)
