"""Cart tests against saucedemo.com."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage


@allure.feature("购物车")
@allure.story("加入再移除")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_then_remove_item_from_cart(inventory):
    """Adding then removing an item leaves the cart empty."""
    inventory.add_item_to_cart(0)
    assert inventory.cart_badge_count() == 1

    cart_page = CartPage(inventory.page).open()
    expect(cart_page.cart_items).to_have_count(1)

    cart_page.remove_item(0)
    expect(cart_page.cart_items).to_have_count(0)


@allure.feature("购物车")
@allure.story("跨页面持久化")
@allure.severity(allure.severity_level.NORMAL)
def test_cart_persists_items_across_pages(inventory):
    """Items added on inventory page remain visible after navigating to cart."""
    inventory.add_item_to_cart(0)
    inventory.add_item_to_cart(1)
    assert inventory.cart_badge_count() == 2

    cart_page = CartPage(inventory.page).open()
    expect(cart_page.cart_items).to_have_count(2)

    # Going back to inventory still shows the items as added (button label = "Remove")
    inventory_back = InventoryPage(inventory.page).open()
    expect(inventory_back.remove_buttons).to_have_count(2)
