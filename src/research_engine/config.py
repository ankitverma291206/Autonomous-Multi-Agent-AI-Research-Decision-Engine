"""Application settings loaded from environment variables."""

import os


def setting(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


DATABASE_URL = setting("DATABASE_URL", "sqlite:///./data/reports.db")
LLM_PROVIDER = setting("LLM_PROVIDER", "demo").lower()
LLM_BASE_URL = setting("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
LLM_API_KEY = setting("LLM_API_KEY", "")
LLM_MODEL = setting("LLM_MODEL", "gpt-4o-mini")
FRONTEND_ORIGIN = setting("FRONTEND_ORIGIN", "http://localhost:3000")
