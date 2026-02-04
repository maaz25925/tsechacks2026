from __future__ import annotations

from typing import Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 🔥 prevents crashes from unused .env vars
    )

    # =========================
    # Supabase
    # =========================
    supabase_url: str | None = None
    supabase_key: str | None = None
    supabase_videos_bucket: str = "videos"

    # =========================
    # AI Providers
    # =========================
    groq_api_key: str | None = None
    openai_api_key: str | None = None

    groq_base_url: str = "https://api.groq.com/openai/v1"
    openai_base_url: str = "https://api.openai.com/v1"

    ai_model: str = "llama-3.1-8b-instant"
    openai_fallback_model: str = "gpt-4o-mini"

    # =========================
    # Finternet (mock service)
    # =========================
    finternet_base: str | None = None
    finternet_key: str | None = None

    # =========================
    # Server
    # =========================
    env: str = "dev"
    log_level: str = "info"
    allowed_origins: List[str] = ["http://localhost:5173"]

    # =========================
    # Payments defaults
    # =========================
    default_reserve_amount: float = 30.0

    # =========================
    # Helpers
    # =========================
    def to_public_dict(self) -> dict[str, Any]:
        return {
            "env": self.env,
            "allowed_origins": self.allowed_origins,
            "supabase_url_set": bool(self.supabase_url),
            "supabase_key_set": bool(self.supabase_key),
            "groq_enabled": bool(self.groq_api_key),
            "openai_enabled": bool(self.openai_api_key),
            "videos_bucket": self.supabase_videos_bucket,
        }


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
