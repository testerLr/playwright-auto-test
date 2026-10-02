"""Inventory tests against saucedemo.com."""

from __future__ import annotations

import allure

EXPECTED_ITEM_COUNT = 6


@allure.feature("商品列表")
@allure.story("默认加载")
@allure.severity(allure.severity_level.NORMAL)
def test_inventory_loads_after_login(inventory):
    """After login, the inventory shows the expected number of items."""
    assert inventory.item_count() == EXPECTED_ITEM_COUNT


@allure.feature("商品列表")
@allure.story("价格升序排序")
@allure.severity(allure.severity_level.NORMAL)
def test_sort_by_price_low_to_high(inventory):
    """Sorting by price low-to-high puts the cheapest item first."""
    inventory.sort_by("lohi")

    first_price_text = inventory.inventory_items.first.locator(
        ".inventory_item_price"
    ).text_content()
    assert first_price_text is not None
    first_price = float(first_price_text.replace("$", ""))

    all_prices = [
        float(
            (p or "").replace("$", "")
        )
        for p in inventory.inventory_items.locator(".inventory_item_price").all_text_contents()
    ]
    assert all_prices == sorted(all_prices)
    assert first_price == min(all_prices)


@allure.feature("商品列表")
@allure.story("加入购物车")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_to_cart_updates_badge(inventory):
    """Clicking 'Add to cart' on the first item updates the badge to '1'."""
    inventory.add_item_to_cart(0)
    assert inventory.cart_badge_count() == 1
