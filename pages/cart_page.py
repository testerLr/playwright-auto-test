"""Cart page object for https://www.saucedemo.com/cart.html."""

from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    """Sauce Demo shopping cart page."""

    URL = "/cart.html"

    # ----- Locators -----

    @property
    def cart_items(self):
        return self.page.locator(".cart_item")

    @property
    def continue_shopping_button(self):
        return self.page.locator('[data-test="continue-shopping"]')

    @property
    def checkout_button(self):
        return self.page.locator('[data-test="checkout"]')

    @property
    def remove_buttons(self):
        return self.page.locator('button[data-test^="remove"]')

    # ----- High-level actions -----

    def open(self) -> "CartPage":
        """Navigate to the cart page and return self for chaining."""
        self.goto(self.URL)
        return self

    def remove_item(self, index: int) -> None:
        """Click the ``remove`` button at the given (0-based) index."""
        self.remove_buttons.nth(index).click()

    def item_count(self) -> int:
        return self.cart_items.count()

    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()