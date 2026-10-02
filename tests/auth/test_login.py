"""Auth tests against saucedemo.com."""

from __future__ import annotations

import allure
from playwright.sync_api import expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@allure.feature("登录")
@allure.story("成功登录")
@allure.severity(allure.severity_level.CRITICAL)
def test_login_with_valid_credentials(page, auth_credentials):
    """Logging in with the public standard_user credentials lands on /inventory.html."""
    username, password = auth_credentials
    login_page = LoginPage(page).open()
    login_page.login(username, password)

    page.wait_for_url("**/inventory.html", wait_until="load")
    inventory = InventoryPage(page)
    expect(inventory.title).to_have_text("Products")


@allure.feature("登录")
@allure.story("错误凭据")
@allure.severity(allure.severity_level.NORMAL)
def test_login_with_invalid_credentials(page):
    """A wrong password shows the locked-out error banner."""
    login_page = LoginPage(page).open()
    login_page.login("standard_user", "wrong_password")

    login_page.expect_error("do not match")


@allure.feature("登录")
@allure.story("登出")
@allure.severity(allure.severity_level.NORMAL)
def test_logout(logged_in_page):
    """Logging out from the menu returns to the login page."""
    page = logged_in_page

    page.click("#react-burger-menu-btn")
    page.click('[data-test="logout-sidebar-link"]')

    page.wait_for_url("**/", wait_until="load")
    assert "saucedemo.com" in page.url
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
