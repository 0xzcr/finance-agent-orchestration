"""
Crew runner — executes the investment crew with Cerebras LLM and Zerodha tools.
"""

import os
import sys
from pathlib import Path

from crewai import Agent, Crew, Process, Task

from app.config import settings
from app.cerebras_llm import configure_cerebras, get_cerebras_llm_config


# Add finance_agents source to path for tool imports
FINANCE_AGENTS_SRC = Path(__file__).parent.parent.parent / "finance_agents" / "src"
sys.path.insert(0, str(FINANCE_AGENTS_SRC))


def _get_tools(market: str = "india"):
    """Get appropriate market tools based on target market."""
    tools = []

    if market == "india" and settings.KITE_ACCESS_TOKEN:
        from finance_agents.tools.zerodha_tool import (
            ZerodhaQuoteTool,
            ZerodhaHoldingsTool,
            ZerodhaHistoricalTool,
        )
        tools = [ZerodhaQuoteTool(), ZerodhaHoldingsTool(), ZerodhaHistoricalTool()]
    else:
        from finance_agents.tools.market_data_tool import (
            StockQuoteTool,
            MarketNewsTool,
            TopMoversTool,
            CompanyOverviewTool,
        )
        tools = [StockQuoteTool(), MarketNewsTool(), TopMoversTool(), CompanyOverviewTool()]

    return tools


def run_investment_crew(
    user_prompt: str,
    investment_amount: str = "10000",
    risk_tolerance: str = "moderate",
    market: str = "india",
) -> str:
    """
    Run the 4-agent investment crew based on the user's prompt.

    Args:
        user_prompt: What the user wants to invest in (e.g., "AI stocks in India")
        investment_amount: How much to invest
        risk_tolerance: conservative / moderate / aggressive
        market: india (uses Zerodha) or global (uses Alpha Vantage)

    Returns:
        Final investment recommendation as markdown string
    """
    # Configure Cerebras as the LLM
    configure_cerebras()
    llm_model = get_cerebras_llm_config()

    # Set Zerodha credentials in env
    os.environ["KITE_API_KEY"] = settings.KITE_API_KEY
    os.environ["KITE_ACCESS_TOKEN"] = settings.KITE_ACCESS_TOKEN
    os.environ["ALPHA_VANTAGE_API_KEY"] = settings.ALPHA_VANTAGE_API_KEY

    # Get market-appropriate tools
    market_tools = _get_tools(market)

    # --- Define Agents ---

    market_researcher = Agent(
        role="Market Research Analyst",
        goal=(
            f"Research current market conditions and find the best investment "
            f"opportunities based on: {user_prompt}"
        ),
        backstory=(
            "You are a senior market research analyst with 15 years of experience. "
            "You track global and Indian markets, identify trends, analyze sentiment, "
            "and find high-conviction opportunities backed by data. You always provide "
            "specific numbers: prices, percentages, volumes."
        ),
        tools=market_tools,
        llm=llm_model,
        verbose=True,
    )

    strategy_planner = Agent(
        role="Investment Strategy Planner",
        goal=(
            f"Create an investment strategy for ₹{investment_amount} with "
            f"{risk_tolerance} risk tolerance based on the research findings."
        ),
        backstory=(
            "You are a strategic investment planner managing portfolios worth crores. "
            "You translate research into actionable plans with specific stock picks, "
            "sector allocations, entry points, and position sizing. You always consider "
            "the risk-reward ratio and diversification."
        ),
        tools=market_tools[:2] if len(market_tools) >= 2 else market_tools,
        llm=llm_model,
        verbose=True,
    )

    risk_analyst = Agent(
        role="Risk Assessment Analyst",
        goal=(
            f"Evaluate the investment strategy for risks and ensure it matches "
            f"a {risk_tolerance} risk profile for ₹{investment_amount}."
        ),
        backstory=(
            "You are a quantitative risk analyst who has navigated multiple market "
            "crashes. You analyze volatility, correlation, concentration risk, and "
            "maximum drawdown scenarios. You stress-test strategies and suggest "
            "hedging measures. You are brutally honest about risks."
        ),
        tools=market_tools[:2] if len(market_tools) >= 2 else market_tools,
        llm=llm_model,
        verbose=True,
    )

    portfolio_advisor = Agent(
        role="Portfolio Investment Advisor",
        goal=(
            f"Deliver a final actionable investment plan for ₹{investment_amount} "
            f"with exact allocations, entry prices, targets, and stop-losses."
        ),
        backstory=(
            "You are a certified financial advisor with 20 years of experience. "
            "You synthesize research, strategy, and risk analysis into a clear "
            "investment memo. Your recommendations are always specific — exact "
            "tickers, allocation percentages, entry prices, target prices, and "
            "stop-losses. You communicate clearly and include risk disclaimers."
        ),
        tools=market_tools[:1] if market_tools else [],
        llm=llm_model,
        verbose=True,
    )

    # --- Define Tasks ---

    research_task = Task(
        description=(
            f"Research the following investment request: '{user_prompt}'\n\n"
            f"Investment amount: ₹{investment_amount}\n"
            f"Market: {'Indian (NSE/BSE)' if market == 'india' else 'Global'}\n\n"
            "Gather:\n"
            "1. Current market conditions and sentiment\n"
            "2. Top stocks related to the user's interest with live prices\n"
            "3. Key news and trends affecting this sector\n"
            "4. Fundamental data for the most promising picks\n\n"
            "Be specific with numbers and data."
        ),
        expected_output=(
            "A structured research report with current prices, fundamentals, "
            "news sentiment, and 4-6 specific stock opportunities."
        ),
        agent=market_researcher,
    )

    strategy_task = Task(
        description=(
            f"Based on the research, build an investment strategy for:\n"
            f"- Amount: ₹{investment_amount}\n"
            f"- Risk Tolerance: {risk_tolerance}\n"
            f"- Focus: {user_prompt}\n\n"
            "Include:\n"
            "1. Investment thesis\n"
            "2. Sector allocation (percentages)\n"
            "3. Specific stock picks with entry prices\n"
            "4. Position sizing for each pick\n"
            "5. Entry strategy (SIP vs lumpsum)\n"
            "6. Target prices and timeline"
        ),
        expected_output=(
            "A detailed strategy document with specific allocations, "
            "stock picks, and entry/exit criteria."
        ),
        agent=strategy_planner,
    )

    risk_task = Task(
        description=(
            f"Evaluate the proposed strategy for a {risk_tolerance} risk profile:\n\n"
            "1. Assess volatility risk for each pick\n"
            "2. Check sector concentration\n"
            "3. Identify correlated risks\n"
            "4. Estimate maximum drawdown\n"
            "5. Suggest hedging strategies\n"
            "6. Give a GO/NO-GO with conditions"
        ),
        expected_output=(
            "A risk report with risk score (1-10), per-stock risk assessment, "
            "max drawdown estimate, hedging recommendations, and GO/NO-GO verdict."
        ),
        agent=risk_analyst,
    )

    recommendation_task = Task(
        description=(
            f"Create the final investment recommendation for ₹{investment_amount}:\n\n"
            "Include:\n"
            "1. Executive summary (2-3 lines)\n"
            "2. Portfolio allocation table:\n"
            "   - Stock name & ticker\n"
            "   - Allocation %\n"
            "   - Amount (₹)\n"
            "   - Entry price\n"
            "   - Target price\n"
            "   - Stop-loss\n"
            "3. Implementation steps (what to buy and when)\n"
            "4. Monthly monitoring checklist\n"
            "5. When to rebalance\n"
            "6. Risk disclaimer\n\n"
            "Format as a professional investment memo in markdown."
        ),
        expected_output=(
            "A complete, professional investment memo in markdown with "
            "allocation table, implementation plan, and disclaimers."
        ),
        agent=portfolio_advisor,
    )

    # --- Run Crew ---

    crew = Crew(
        agents=[market_researcher, strategy_planner, risk_analyst, portfolio_advisor],
        tasks=[research_task, strategy_task, risk_task, recommendation_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return result.raw
