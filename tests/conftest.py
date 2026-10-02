"""Global pytest fixtures: settings, credentials, browser context args, login."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage
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
def browser_type_launch_args(app_settings: Settings) -> dict:
    """Browser launch configuration.

    Wires ``app_settings.headless`` (sourced from the ``HEADLESS`` env var
    and the Jenkinsfile ``HEADLESS`` build parameter) into the Playwright
    launch call. ``headless`` MUST live here, not in
    ``browser_context_args``, because pytest-playwright passes the latter
    to ``Browser.new_context()`` which does not accept ``headless``.
    """
    return {"headless": app_settings.headless}


@pytest.fixture(scope="session")
def browser_context_args(app_settings: Settings) -> dict:
    """Browser context configuration: viewport, locale.

    ``base_url`` is intentionally NOT set here: POMs use ``settings.base_url``
    directly, so pytest-base-url's relative-URL machinery is unused.
    """
    return {
        "viewport": {
            "width": app_settings.viewport_width,
            "height": app_settings.viewport_height,
        },
        "locale": "en-US",
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
    # Login lands on /inventory.html; use ``load`` (not ``networkidle``) to
    # avoid the saucedemo networkidle flake (see task-13 in progress.md).
    login_page.page.wait_for_url("**/inventory.html", wait_until="load")
    return page


@pytest.fixture
def inventory(logged_in_page: Page, app_settings: Settings) -> InventoryPage:
    """Return an InventoryPage instance bound to a logged-in page.

    Promoted to the global conftest (was ``tests/inventory/conftest.py``
    in earlier tasks) so cart tests can consume it as a sibling fixture.
    Pytest only propagates conftest.py fixtures to subdirectories, so a
    fixture defined in ``tests/inventory/conftest.py`` was not visible to
    ``tests/cart/test_cart.py``. Mirrors the ``logged_in_page`` move
    from task-10.

    ``Locator.count()`` does not auto-wait, so we explicitly wait for the
    first inventory item to be visible before yielding. This avoids a
    race where the React app has not finished rendering the list yet.
    The wait timeout is one third of ``settings.timeout_ms`` so it scales
    with the configured global timeout instead of being a magic number.
    """
    page = InventoryPage(logged_in_page)
    page.inventory_items.first.wait_for(
        state="visible", timeout=app_settings.timeout_ms // 3
    )
    return page
