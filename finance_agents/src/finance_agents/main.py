#!/usr/bin/env python
"""
Finance Agent Orchestration — Investment Flow

A crew of 4 AI agents that research market trends, plan strategy,
assess risk, and deliver actionable investment recommendations.
"""

from pathlib import Path

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from finance_agents.crews.investment_crew.investment_crew import InvestmentCrew


class InvestmentState(BaseModel):
    focus_area: str = "technology"
    risk_tolerance: str = "moderate"
    time_horizon: str = "6-12 months"
    investment_amount: str = "10000"
    research: str = ""
    strategy: str = ""
    risk_report: str = ""
    recommendation: str = ""


class InvestmentFlow(Flow[InvestmentState]):
    """
    Flow that orchestrates 4 investment agents:
    1. Market Researcher — gathers live market data and news
    2. Strategy Planner — builds an investment thesis and stock picks
    3. Risk Analyst — stress-tests the strategy 
    4. Portfolio Advisor — delivers final actionable recommendation
    """

    @start()
    def gather_inputs(self, crewai_trigger_payload: dict = None):
        print("=" * 60)
        print("  FINANCE AGENT ORCHESTRATION — Investment Flow")
        print("=" * 60)

        if crewai_trigger_payload:
            self.state.focus_area = crewai_trigger_payload.get(
                "focus_area", self.state.focus_area
            )
            self.state.risk_tolerance = crewai_trigger_payload.get(
                "risk_tolerance", self.state.risk_tolerance
            )
            self.state.time_horizon = crewai_trigger_payload.get(
                "time_horizon", self.state.time_horizon
            )
            self.state.investment_amount = crewai_trigger_payload.get(
                "investment_amount", self.state.investment_amount
            )
            print(f"Using trigger payload: {crewai_trigger_payload}")

        print(f"\n  Focus Area:        {self.state.focus_area}")
        print(f"  Risk Tolerance:    {self.state.risk_tolerance}")
        print(f"  Time Horizon:      {self.state.time_horizon}")
        print(f"  Investment Amount: ${self.state.investment_amount}")
        print("=" * 60)

    @listen(gather_inputs)
    def run_investment_crew(self):
        print("\n🚀 Launching Investment Crew...\n")

        inputs = {
            "focus_area": self.state.focus_area,
            "risk_tolerance": self.state.risk_tolerance,
            "time_horizon": self.state.time_horizon,
            "investment_amount": self.state.investment_amount,
        }

        result = InvestmentCrew().crew().kickoff(inputs=inputs)

        self.state.recommendation = result.raw
        print("\n✅ Investment analysis complete!")

    @listen(run_investment_crew)
    def save_recommendation(self):
        print("\n📄 Saving investment recommendation...")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / "investment_recommendation.md"
        with open(output_path, "w") as f:
            f.write(self.state.recommendation)

        print(f"   Saved to {output_path}")
        print("\n" + "=" * 60)
        print("  DONE — Review your recommendation in output/")
        print("=" * 60)


def kickoff():
    """Run the investment flow with default parameters."""
    flow = InvestmentFlow()
    flow.kickoff()


def plot():
    """Generate a visualization of the flow."""
    flow = InvestmentFlow()
    flow.plot()


def run_with_trigger():
    """
    Run the flow with a custom trigger payload.

    Example payload:
    {
        "focus_area": "AI and semiconductors",
        "risk_tolerance": "aggressive",
        "time_horizon": "3-6 months",
        "investment_amount": "25000"
    }
    """
    import json
    import sys

    if len(sys.argv) < 2:
        raise Exception(
            "No trigger payload provided. Pass JSON as argument.\n"
            'Example: run_with_trigger \'{"focus_area": "AI", "investment_amount": "20000"}\''
        )

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    flow = InvestmentFlow()

    try:
        result = flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"Error running flow: {e}")


if __name__ == "__main__":
    kickoff()
