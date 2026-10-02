"""Inventory page object for https://www.saucedemo.com/inventory.html."""

from __future__ import annotations

from typing import Literal

from pages.base_page import BasePage
from utils.config import settings

SortValue = Literal["az", "za", "lohi", "hilo"]


class InventoryPage(BasePage):
    """Sauce Demo inventory (product list) page."""

    URL = "/inventory.html"

    # ----- Locators -----

    @property
    def title(self):
        return self.page.locator('[data-test="title"]')

    @property
    def inventory_container(self):
        return self.page.locator('[data-test="inventory-container"]')

    @property
    def inventory_items(self):
        return self.page.locator(".inventory_item")

    @property
    def sort_dropdown(self):
        return self.page.locator('[data-test="product-sort-container"]')

    @property
    def add_to_cart_buttons(self):
        return self.page.locator('button[data-test^="add-to-cart"]')

    @property
    def cart_badge(self):
        return self.page.locator('[data-test="shopping-cart-badge"]')

    @property
    def remove_buttons(self):
        return self.page.locator('button[data-test^="remove"]')

    # ----- High-level actions -----

    def open(self) -> "InventoryPage":
        """Navigate to the inventory page and return self for chaining."""
        self.goto(self.URL)
        return self

    def add_item_to_cart(self, index: int) -> None:
        """Click the ``add-to-cart`` button at the given (0-based) index."""
        self.add_to_cart_buttons.nth(index).click()

    def remove_item_from_cart(self, index: int) -> None:
        """Click the ``remove`` button at the given (0-based) index."""
        self.page.locator('button[data-test^="remove"]').nth(index).click()

    def sort_by(self, value: SortValue) -> None:
        """Select a sort option in the dropdown."""
        self.sort_dropdown.select_option(value=value)

    def item_count(self) -> int:
        return self.inventory_items.count()

    def cart_badge_count(self) -> int:
        """Return the cart badge number as an int (0 if badge is absent)."""
        # 1s is enough for a state that React updates synchronously after a
        # click; it scales off settings.timeout_ms so global timeout changes
        # propagate here too.
        text = self.cart_badge.text_content(timeout=settings.timeout_ms // 30) or "0"
        return int(text)
