"""Inventory-domain conftest: provides an InventoryPage after login."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage


@pytest.fixture
def inventory(logged_in_page: Page) -> InventoryPage:
    """Return an InventoryPage instance bound to a logged-in page.

    ``Locator.count()`` does not auto-wait, so we explicitly wait for the
    first inventory item to be visible before yielding. This avoids a
    race where the React app has not finished rendering the list yet.
    """
    page = InventoryPage(logged_in_page)
    page.inventory_items.first.wait_for(state="visible", timeout=10000)
    return page
