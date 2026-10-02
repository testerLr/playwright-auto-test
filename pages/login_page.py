"""Login page object for https://www.saucedemo.com/."""

from __future__ import annotations

from playwright.sync_api import Page
from playwright.sync_api import expect as playwright_expect

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Sauce Demo login page."""

    URL = "/"

    # ----- Locators (lazy via @property) -----

    @property
    def username_input(self):
        return self.page.locator('[data-test="username"]')

    @property
    def password_input(self):
        return self.page.locator('[data-test="password"]')

    @property
    def login_button(self):
        return self.page.locator('[data-test="login-button"]')

    @property
    def error_message(self):
        return self.page.locator('[data-test="error"]')

    # ----- High-level actions -----

    def open(self) -> "LoginPage":
        """Navigate to the login page and return self for chaining."""
        self.goto(self.URL)
        return self

    def login(self, username: str, password: str) -> None:
        """Fill credentials and click the login button."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def expect_error(self, text: str) -> None:
        """Assert the error banner contains ``text``."""
        playwright_expect(self.error_message).to_contain_text(text)
