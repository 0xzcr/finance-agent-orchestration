# Finance Agents — Investment Crew

A CrewAI-powered investment orchestration system with 4 specialized AI agents that research live market data, plan strategy, assess risk, and deliver actionable investment recommendations.

## Agents

| # | Agent | Role | Tools |
|---|-------|------|-------|
| 1 | **Market Researcher** | Gathers live market data, news sentiment, top movers | Stock Quote, Market News, Top Gainers/Losers, Company Overview |
| 2 | **Strategy Planner** | Builds investment thesis, picks stocks, defines allocations | Stock Quote, Company Overview |
| 3 | **Risk Analyst** | Stress-tests the strategy, identifies downside scenarios | Stock Quote, Company Overview |
| 4 | **Portfolio Advisor** | Delivers final recommendation with specific allocations | Stock Quote |

## Flow

```
gather_inputs → run_investment_crew → save_recommendation
                     │
                     ├─ Market Research Task
                     ├─ Strategy Planning Task
                     ├─ Risk Assessment Task
                     └─ Investment Recommendation Task
```

## Setup

1. **Install dependencies:**

```bash
cd finance_agents
pip install -e .
```

2. **Set API keys in `.env`:**

```env
OPENAI_API_KEY=your_openai_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

Get a free Alpha Vantage API key at: https://www.alphavantage.co/support/#api-key

3. **Run the investment flow:**

```bash
# Default: technology focus, moderate risk, $10k, 6-12 month horizon
kickoff

# Custom parameters via trigger payload
run_with_trigger '{"focus_area": "AI and semiconductors", "risk_tolerance": "aggressive", "time_horizon": "3-6 months", "investment_amount": "25000"}'
```

## Configuration Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| `focus_area` | `technology` | Any sector/theme: "AI", "healthcare", "energy", "crypto", etc. |
| `risk_tolerance` | `moderate` | `conservative`, `moderate`, `aggressive` |
| `time_horizon` | `6-12 months` | Any timeframe: "1-3 months", "1-2 years", etc. |
| `investment_amount` | `10000` | Any dollar amount |

## Output

The final investment recommendation is saved to `output/investment_recommendation.md` and includes:

- Executive summary
- Portfolio allocation table (tickers, amounts, targets, stop-losses)
- Implementation timeline
- Monitoring checklist
- Risk disclaimer

## Market Data Tools

All tools use the [Alpha Vantage API](https://www.alphavantage.co/):

- **Stock Quote** — Real-time price, volume, change %
- **Market News & Sentiment** — Headlines with AI sentiment scores, filterable by ticker/topic
- **Top Gainers/Losers** — Daily market movers and most active stocks
- **Company Overview** — Fundamentals: P/E, EPS, market cap, margins, 52-week range

## Disclaimer

This system generates AI-powered investment analysis for educational and informational purposes only. It does not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.
