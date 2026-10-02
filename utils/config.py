"""Application settings loaded from .env via pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Target site
    base_url: str = "https://www.saucedemo.com"

    # Sauce Demo public credentials (replace for your own site)
    sauce_username: str = "standard_user"
    sauce_password: str = "secret_sauce"

    # Browser behavior
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000


settings = Settings()
