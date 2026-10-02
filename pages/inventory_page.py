"""Inventory page object for https://www.saucedemo.com/inventory.html."""

from __future__ import annotations

from typing import Literal

from playwright.sync_api import Page

from pages.base_page import BasePage

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

    # ----- High-level actions -----

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
        text = self.cart_badge.text_content(timeout=1000) or "0"
        return int(text)
