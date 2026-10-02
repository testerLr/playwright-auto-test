"""Global pytest fixtures: settings, credentials, browser context args."""

from __future__ import annotations

import pytest

from utils.config import Settings, settings


@pytest.fixture(scope="session")
def app_settings() -> Settings:
    """Session-scoped Settings instance."""
    return settings


@pytest.fixture(scope="session")
def auth_credentials(app_settings: Settings) -> tuple[str, str]:
    """Sauce Demo login credentials loaded from settings."""
    return app_settings.sauce_username, app_settings.sauce_password


@pytest.fixture(scope="session")
def browser_context_args(app_settings: Settings) -> dict:
    """Browser context configuration: viewport, locale, base URL."""
    return {
        "viewport": {
            "width": app_settings.viewport_width,
            "height": app_settings.viewport_height,
        },
        "locale": "en-US",
        "base_url": app_settings.base_url,
    }