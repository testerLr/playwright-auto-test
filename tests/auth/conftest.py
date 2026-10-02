"""Auth-domain conftest: provides a logged-in Playwright page."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage


@pytest.fixture
def logged_in_page(page: Page, auth_credentials: tuple[str, str]) -> Page:
    """Return a Playwright Page already logged in to saucedemo.com."""
    username, password = auth_credentials
    login_page = LoginPage(page).open()
    login_page.login(username, password)
    # Login lands on /inventory.html; wait until DOM is stable.
    login_page.page.wait_for_url("**/inventory.html", wait_until="networkidle")
    return page