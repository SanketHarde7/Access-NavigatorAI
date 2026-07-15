"""
Access Navigator AI - Configuration Management
===============================================
Centralized config for stadium navigation AI system.
Supports multiple LLM providers, stadium configs, and feature flags.
"""
import os
from pydantic_settings import BaseSettings


def _csv_env(name: str, default: str) -> list[str]:
    """Parse comma-separated env vars without falling back to wildcard CORS defaults."""
    return [value.strip() for value in os.environ.get(name, default).split(",") if value.strip()]


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Keys
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")

    # LLM Configuration
    PRIMARY_LLM: str = "gemini"  # groq, gemini, openai
    FALLBACK_LLM: str = "groq"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2048

    # Model IDs
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_FALLBACK_MODEL: str = "mixtral-8x7b-32768"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = int(os.environ.get("PORT", 8000))
    DEBUG: bool = False
    # Security: explicit browser origins satisfy scanner-safe CORS while preserving local dev and the PromptWars Vercel demo.
    CORS_ORIGINS: list[str] = _csv_env(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,https://access-navigator-ai.vercel.app",
    )

    # Features
    ENABLE_STREAMING: bool = True
    ENABLE_VOICE_INPUT: bool = True
    ENABLE_PREDICTIONS: bool = True
    ENABLE_ANALYTICS: bool = True
    ENABLE_CONVERSATIONAL_AI: bool = True

    # Data Refresh
    ZONE_REFRESH_INTERVAL_MS: int = 5000
    PREDICTION_HORIZON_MINUTES: int = 30

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
        case_sensitive = True


settings = Settings()
