"""Base page object — shared utilities for all page objects."""

from __future__ import annotations

import allure
from playwright.sync_api import Page

from utils.config import settings


class BasePage:
    """All concrete page objects inherit from this.

    Holds only generic helpers (navigation, screenshot, current URL).
    Domain actions and locators live in subclasses.
    """

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, path: str = "/") -> None:
        """Navigate to a path appended to settings.base_url.

        Uses ``wait_until="load"`` so locators resolved immediately after
        the call observe a stable DOM. ``networkidle`` was flaky against
        saucedemo (see task-13 in progress.md), so the scaffold uses
        ``load`` and lets locators auto-wait for individual elements.
        """
        url = settings.base_url.rstrip("/") + path
        self.page.goto(url, wait_until="load")

    def screenshot(self, name: str) -> None:
        """Capture a full-page screenshot and attach to the Allure report."""
        allure.attach(
            self.page.screenshot(full_page=True),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )

    @property
    def current_url(self) -> str:
        return self.page.url
