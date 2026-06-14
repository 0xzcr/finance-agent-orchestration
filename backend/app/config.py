"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Cerebras LLM
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    CEREBRAS_MODEL: str = os.getenv("CEREBRAS_MODEL", "llama-4-scout-17b-16e-instruct")

    # Zerodha Kite Connect
    KITE_API_KEY: str = os.getenv("KITE_API_KEY", "")
    KITE_API_SECRET: str = os.getenv("KITE_API_SECRET", "")
    KITE_ACCESS_TOKEN: str = os.getenv("KITE_ACCESS_TOKEN", "")

    # Alpha Vantage (global market data fallback)
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")

    # App
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
