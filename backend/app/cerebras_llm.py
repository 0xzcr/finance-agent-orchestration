"""
Cerebras LLM integration for CrewAI.

Cerebras uses an OpenAI-compatible API, so we configure CrewAI's LLM
to point to Cerebras's inference endpoint.
"""

import os
from app.config import settings


def configure_cerebras():
    """
    Configure environment variables so CrewAI uses Cerebras as the LLM provider.

    CrewAI supports LiteLLM under the hood, which means we can use the
    cerebras/ prefix to route to Cerebras inference.
    """
    # Set Cerebras API key for the SDK
    os.environ["CEREBRAS_API_KEY"] = settings.CEREBRAS_API_KEY

    # For CrewAI's LiteLLM integration — uses cerebras/ prefix
    os.environ["OPENAI_API_KEY"] = settings.CEREBRAS_API_KEY
    os.environ["OPENAI_API_BASE"] = "https://api.cerebras.ai/v1"


def get_cerebras_llm_config() -> str:
    """
    Return the model string that CrewAI/LiteLLM uses to route to Cerebras.

    Available Cerebras models:
    - llama-4-scout-17b-16e-instruct (fast, good for most tasks)
    - llama3.1-8b (fastest)
    - llama3.1-70b (best quality)
    """
    return f"cerebras/{settings.CEREBRAS_MODEL}"
