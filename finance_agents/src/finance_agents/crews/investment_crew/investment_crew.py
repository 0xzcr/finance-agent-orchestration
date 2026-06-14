from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from finance_agents.tools.market_data_tool import (
    CompanyOverviewTool,
    MarketNewsTool,
    StockQuoteTool,
    TopMoversTool,
)


@CrewBase
class InvestmentCrew:
    """Investment Crew — 4 agents that research, plan, assess risk, and recommend investments."""

    agents: list[BaseAgent]
    tasks: list[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["market_researcher"],  # type: ignore[index]
            tools=[
                StockQuoteTool(),
                MarketNewsTool(),
                TopMoversTool(),
                CompanyOverviewTool(),
            ],
            verbose=True,
        )

    @agent
    def strategy_planner(self) -> Agent:
        return Agent(
            config=self.agents_config["strategy_planner"],  # type: ignore[index]
            tools=[
                StockQuoteTool(),
                CompanyOverviewTool(),
            ],
            verbose=True,
        )

    @agent
    def risk_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["risk_analyst"],  # type: ignore[index]
            tools=[
                StockQuoteTool(),
                CompanyOverviewTool(),
            ],
            verbose=True,
        )

    @agent
    def portfolio_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config["portfolio_advisor"],  # type: ignore[index]
            tools=[
                StockQuoteTool(),
            ],
            verbose=True,
        )

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config["market_research_task"],  # type: ignore[index]
        )

    @task
    def strategy_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config["strategy_planning_task"],  # type: ignore[index]
        )

    @task
    def risk_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config["risk_assessment_task"],  # type: ignore[index]
        )

    @task
    def investment_recommendation_task(self) -> Task:
        return Task(
            config=self.tasks_config["investment_recommendation_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Investment Crew with sequential process."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
