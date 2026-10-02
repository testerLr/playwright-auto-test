"""Global pytest fixtures: settings, credentials, browser context args, login."""

from __future__ import annotations

import pytest

from pages.login_page import LoginPage
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


@pytest.fixture
def logged_in_page(page, auth_credentials: tuple[str, str]):
    """Return a Playwright Page already logged in to saucedemo.com.

    Moved to the global conftest so that tests in any subdirectory
    (auth/, inventory/, cart/) can consume it without redefinition.
    Per spec §7.3 it is a function-scoped fixture in the same tier
    as ``page`` and ``auth_credentials``.
    """
    username, password = auth_credentials
    login_page = LoginPage(page).open()
    login_page.login(username, password)
    # Login lands on /inventory.html; wait until DOM is stable.
    login_page.page.wait_for_url("**/inventory.html", wait_until="networkidle")
    return page
