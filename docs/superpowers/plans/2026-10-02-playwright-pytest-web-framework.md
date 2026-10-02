# Playwright + pytest Web 自动化框架 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个可复用的 Playwright + pytest Web 自动化脚手架,目录与样板代码完整,8 个针对 saucedemo.com 的示例测试全部通过,Allure 报告与并行执行可用,Jenkinsfile 开箱可跑。

**Architecture:** 扁平 `pages/` + 层级 conftest;`pyproject.toml` 集中配置 + `.env` 存密钥;每层 fixture 显式声明依赖;强制 POM,选择器走 `data-test`。

**Tech Stack:** Python 3.12, uv, Playwright(Chromium only), pytest, pytest-playwright, pytest-xdist, allure-pytest, pydantic-settings, ruff

---

## Global Constraints

复制自 spec,所有任务隐式遵循:

- **Python**: `>=3.12,<3.13`
- **浏览器**: 仅 Chromium(不安装 Firefox/WebKit)
- **依赖管理**: uv,锁文件 `uv.lock` 入库
- **POM 强制**: 所有页面对象继承 `BasePage`,locator 用 `@property`,选择器优先 `data-test`
- **配置**: `pyproject.toml`(静态)+ `.env`(运行时密钥,不入库)
- **并行**: pytest-xdist,默认 `-n=auto --dist=loadfile`
- **失败产物**: `--screenshot=only-on-failure --tracing=retain-on-failure`,不开 video
- **报告**: Allure,原始数据写 `reports/allure-results/`
- **CI**: Jenkinsfile,6 个 stage:Checkout → Setup → Install → Test → Report → Archive
- **示例**: 8 个测试,目标 https://www.saucedemo.com,账号 `standard_user` / `secret_sauce`
- **Fixture 命名**: `*_page` 返回 Playwright `Page`;不带 `_page` 后缀的(如 `inventory`)返回 POM 对象

---

## 文件结构(任务完成后的目标状态)

```
playwright-auto-test/
├── pyproject.toml
├── uv.lock                          # uv 生成
├── .env.example
├── .gitignore                       # 已存在,需补 playwright/pytest 输出项
├── Jenkinsfile
├── README.md
├── pages/
│   ├── __init__.py
│   ├── base_page.py
│   ├── login_page.py
│   ├── inventory_page.py
│   └── cart_page.py
├── utils/
│   ├── __init__.py
│   ├── config.py
│   └── helpers.py                   # 占位,本计划不写实质内容
├── tests/
│   ├── __init__.py                  # 空文件
│   ├── conftest.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_login.py
│   ├── inventory/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── test_inventory.py
│   └── cart/
│       ├── __init__.py
│       └── test_cart.py
└── reports/                         # 自动生成,.gitignore 已排除
    └── allure-results/
```

---

## Task 1: uv 项目初始化与依赖声明

**Files:**
- Create: `pyproject.toml`
- Create: `.env.example`
- Create: `pages/__init__.py`(空)
- Create: `utils/__init__.py`(空)

**Interfaces:**
- Produces: `pyproject.toml` 提供 `playwright`/`pytest-playwright`/`pytest-xdist`/`allure-pytest`/`pydantic-settings`/`python-dotenv`/`pytest`/`ruff`;`requires-python = ">=3.12,<3.13"`

- [ ] **Step 1.1: 初始化 uv 项目**

```bash
cd F:/project/git/playwright-auto-test
uv init --no-readme --no-pin-python --bare
```

预期:`pyproject.toml` 已被创建(uv 默认骨架,会被后面步骤覆盖)。

- [ ] **Step 1.2: 覆盖 pyproject.toml**

将 `pyproject.toml` 内容替换为以下完整版本(覆盖 uv 默认生成的):

```toml
[project]
name = "playwright-auto-test"
version = "0.1.0"
description = "Reusable Playwright + pytest web automation scaffold"
requires-python = ">=3.12,<3.13"
dependencies = [
    "playwright>=1.40",
    "pytest>=8.0",
    "pytest-playwright>=0.5",
    "pytest-xdist>=3.5",
    "allure-pytest>=2.13",
    "pydantic-settings>=2.0",
    "python-dotenv>=1.0",
]

[dependency-groups]
dev = [
    "ruff>=0.6",
    "pytest>=8.0",
]

[tool.uv]
package = false

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--alluredir=reports/allure-results",
    "-n=auto",
    "--dist=loadfile",
    "--screenshot=only-on-failure",
    "--tracing=retain-on-failure",
]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "smoke: smoke tests",
    "regression: regression tests",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

- [ ] **Step 1.3: 创建空包目录的 `__init__.py`**

```bash
cd F:/project/git/playwright-auto-test
touch pages/__init__.py utils/__init__.py
```

在 Windows 上如果 `touch` 不可用,用:
```bash
echo. > pages/__init__.py
echo. > utils/__init__.py
```

预期:两个空文件存在。

- [ ] **Step 1.4: 创建 `.env.example`**

写入完整内容:

```dotenv
# Sauce Demo public credentials (replace for your own site)
SAUCE_USERNAME=standard_user
SAUCE_PASSWORD=secret_sauce

# Target site
BASE_URL=https://www.saucedemo.com

# Browser behavior
HEADLESS=true
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720
TIMEOUT_MS=30000

# Allure output directory
ALLURE_RESULTS_DIR=reports/allure-results
```

- [ ] **Step 1.5: 同步依赖**

```bash
cd F:/project/git/playwright-auto-test
uv sync
```

预期:命令成功,生成 `uv.lock` 与 `.venv/`。`.venv/` 已被 `.gitignore` 排除。

- [ ] **Step 1.6: 验证 ruff 配置生效**

```bash
cd F:/project/git/playwright-auto-test
uv run ruff check .
```

预期:无错误(项目目前还是空代码)。

- [ ] **Step 1.7: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add pyproject.toml .env.example pages/__init__.py utils/__init__.py
git commit -m "chore: bootstrap uv project with deps and ruff config"
```

---

## Task 2: 安装 Chromium 浏览器

**Files:**
- Modify: `uv.lock`(uv 自动更新)

**Interfaces:**
- Produces: 可在 `uv run` 下启动 Chromium 的 playwright 运行时

- [ ] **Step 2.1: 安装 Chromium**

```bash
cd F:/project/git/playwright-auto-test
uv run playwright install chromium
```

预期:下载并安装 Chromium。耗时较长,首次约 100–200 MB。

- [ ] **Step 2.2: 验证 playwright 可用**

```bash
cd F:/project/git/playwright-auto-test
uv run playwright --version
```

预期:输出版本号(如 `Version 1.49.x`)。

- [ ] **Step 2.3: Commit(锁文件)**

```bash
cd F:/project/git/playwright-auto-test
git add uv.lock
git commit -m "chore: install chromium browser and update uv.lock"
```

注意:`uv.lock` 因 `uv run playwright install` 触发环境变化,可能在某些版本需要重新 `uv sync` 才能反映。

---

## Task 3: 配置层(utils/config.py)

**Files:**
- Create: `utils/config.py`

**Interfaces:**
- Produces: `utils.config.settings` 单例 —— `Settings` 实例,从 `.env` 加载,字段:`base_url`、`sauce_username`、`sauce_password`、`headless`、`viewport_width`、`viewport_height`、`timeout_ms`、`allure_results_dir`

- [ ] **Step 3.1: 创建 `utils/config.py`**

写入完整内容:

```python
"""Application settings loaded from .env via pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration sourced from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Target site
    base_url: str = "https://www.saucedemo.com"

    # Sauce Demo public credentials (replace for your own site)
    sauce_username: str = "standard_user"
    sauce_password: str = "secret_sauce"

    # Browser behavior
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000

    # Allure output
    allure_results_dir: str = "reports/allure-results"


settings = Settings()
```

- [ ] **Step 3.2: 本地复制 `.env.example` 为 `.env`(不进库)**

```bash
cd F:/project/git/playwright-auto-test
cp .env.example .env
```

Windows 等价:`copy .env.example .env`。

- [ ] **Step 3.3: 验证 settings 可导入且字段读取正确**

```bash
cd F:/project/git/playwright-auto-test
uv run python -c "from utils.config import settings; print(settings.base_url, settings.sauce_username)"
```

预期:`https://www.saucedemo.com standard_user`

- [ ] **Step 3.4: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add utils/config.py
git commit -m "feat(utils): add pydantic-settings based config loader"
```

---

## Task 4: BasePage

**Files:**
- Create: `pages/base_page.py`

**Interfaces:**
- Produces: `pages.base_page.BasePage(page: Page)` —— 提供 `goto(path: str = "/")`、`screenshot(name: str)`、`current_url` 属性
- 依赖 `utils.config.settings.base_url`

- [ ] **Step 4.1: 创建 `pages/base_page.py`**

写入完整内容:

```python
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

        Uses ``wait_until="networkidle"`` so locators resolved immediately
        after the call observe a stable DOM.
        """
        url = settings.base_url.rstrip("/") + path
        self.page.goto(url, wait_until="networkidle")

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
```

- [ ] **Step 4.2: 验证可导入**

```bash
cd F:/project/git/playwright-auto-test
uv run python -c "from pages.base_page import BasePage; print(BasePage.__name__)"
```

预期:`BasePage`

- [ ] **Step 4.3: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add pages/base_page.py
git commit -m "feat(pages): add BasePage with goto, screenshot, current_url"
```

---

## Task 5: LoginPage

**Files:**
- Create: `pages/login_page.py`

**Interfaces:**
- Produces: `pages.login_page.LoginPage(BasePage)` —— locators:`username_input`、`password_input`、`login_button`、`error_message`(均为 `@property` 返回 `Locator`);方法:`open() -> LoginPage`、`login(username: str, password: str) -> None`

- [ ] **Step 5.1: 创建 `pages/login_page.py`**

写入完整内容:

```python
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
```

- [ ] **Step 5.2: 验证可导入**

```bash
cd F:/project/git/playwright-auto-test
uv run python -c "from pages.login_page import LoginPage; print(LoginPage.__name__)"
```

预期:`LoginPage`

- [ ] **Step 5.3: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add pages/login_page.py
git commit -m "feat(pages): add LoginPage for saucedemo.com"
```

---

## Task 6: InventoryPage

**Files:**
- Create: `pages/inventory_page.py`

**Interfaces:**
- Produces: `pages.inventory_page.InventoryPage(BasePage)` —— locators:`title`、`inventory_container`、`inventory_items`、`sort_dropdown`、`add_to_cart_buttons`、`cart_badge`;方法:`add_item_to_cart(index: int)`、`remove_item_from_cart(index: int)`、`sort_by(value: str)`、`item_count() -> int`、`cart_badge_count() -> int`

- [ ] **Step 6.1: 创建 `pages/inventory_page.py`**

写入完整内容:

```python
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
```

- [ ] **Step 6.2: 验证可导入**

```bash
cd F:/project/git/playwright-auto-test
uv run python -c "from pages.inventory_page import InventoryPage; print(InventoryPage.__name__)"
```

预期:`InventoryPage`

- [ ] **Step 6.3: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add pages/inventory_page.py
git commit -m "feat(pages): add InventoryPage for saucedemo.com"
```

---

## Task 7: CartPage

**Files:**
- Create: `pages/cart_page.py`

**Interfaces:**
- Produces: `pages.cart_page.CartPage(BasePage)` —— locators:`cart_items`、`continue_shopping_button`、`checkout_button`、`remove_buttons`;方法:`remove_item(index: int)`、`item_count() -> int`、`continue_shopping() -> None`

- [ ] **Step 7.1: 创建 `pages/cart_page.py`**

写入完整内容:

```python
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

    def remove_item(self, index: int) -> None:
        """Click the ``remove`` button at the given (0-based) index."""
        self.remove_buttons.nth(index).click()

    def item_count(self) -> int:
        return self.cart_items.count()

    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()
```

- [ ] **Step 7.2: 验证可导入**

```bash
cd F:/project/git/playwright-auto-test
uv run python -c "from pages.cart_page import CartPage; print(CartPage.__name__)"
```

预期:`CartPage`

- [ ] **Step 7.3: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add pages/cart_page.py
git commit -m "feat(pages): add CartPage for saucedemo.com"
```

---

## Task 8: 顶层 conftest 与 pytest 收集配置

**Files:**
- Create: `tests/__init__.py`(空)
- Create: `tests/conftest.py`

**Interfaces:**
- Produces: `tests.conftest` 提供 fixture:
  - `settings`(session) → `Settings` 实例
  - `auth_credentials`(session) → `(str, str)` 用户名/密码元组
  - `browser_context_args`(session) → dict,注入 viewport、locale
- `tests/` 可被 pytest 识别

- [ ] **Step 8.1: 创建 `tests/__init__.py`**

```bash
cd F:/project/git/playwright-auto-test
echo. > tests/__init__.py
```

预期:`tests/__init__.py` 存在(空文件)。

- [ ] **Step 8.2: 创建 `tests/conftest.py`**

写入完整内容:

```python
"""Global pytest fixtures: settings, credentials, browser context args."""

from __future__ import annotations

import pytest

from utils.config import Settings, settings


@pytest.fixture(scope="session")
def app_settings() -> Settings:
    """Session-scoped Settings instance."""
    return settings


@pytest.fixture(scope="session")
def auth_credentials(app_settings: Settings) -> tuple[str, str]:
    """Sauce Demo login credentials loaded from settings."""
    return app_settings.sauce_username, app_settings.sauce_password


@pytest.fixture(scope="session")
def browser_context_args(app_settings: Settings) -> dict:
    """Browser context configuration: viewport, locale, base URL."""
    return {
        "viewport": {
            "width": app_settings.viewport_width,
            "height": app_settings.viewport_height,
        },
        "locale": "en-US",
        "base_url": app_settings.base_url,
    }
```

- [ ] **Step 8.3: 验证 pytest 可收集项目(此时无测试,应提示 collected 0 items)**

```bash
cd F:/project/git/playwright-auto-test
uv run pytest --co -q
```

预期:输出 `collected 0 items`,无错误。

- [ ] **Step 8.4: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add tests/__init__.py tests/conftest.py
git commit -m "feat(tests): add global conftest with settings/credentials fixtures"
```

---

## Task 9: Auth 测试 —— conftest + 第一个测试(TDD)

**Files:**
- Create: `tests/auth/__init__.py`(空)
- Create: `tests/auth/conftest.py`
- Create: `tests/auth/test_login.py`(3 个测试)

**Interfaces:**
- Produces fixture `logged_in_page`(function) → playwright `Page`,登录已完成
- Produces 3 个测试:
  - `test_login_with_valid_credentials` —— 登录后跳到 inventory
  - `test_login_with_invalid_credentials` —— 错误密码显示提示
  - `test_logout` —— 登录后菜单登出回到登录页

- [ ] **Step 9.1: 创建 `tests/auth/__init__.py`**

```bash
cd F:/project/git/playwright-auto-test
echo. > tests/auth/__init__.py
```

- [ ] **Step 9.2: 创建 `tests/auth/conftest.py`**

写入完整内容:

```python
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
```

- [ ] **Step 9.3: 创建 `tests/auth/test_login.py`**

写入完整内容:

```python
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

    page.wait_for_url("**/inventory.html", wait_until="networkidle")
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

    page.wait_for_url("**/", wait_until="networkidle")
    assert "saucedemo.com" in page.url
    expect(page.locator('[data-test="login-button"]')).to_be_visible()
```

- [ ] **Step 9.4: 运行 auth 测试套件**

```bash
cd F:/project/git/playwright-auto-test
uv run pytest tests/auth/ -v
```

预期:3 个测试全部 PASS。如有失败,优先排查:
- 网络问题 → `curl -I https://www.saucedemo.com`
- 选择器变化 → 检查 saucedemo.com 是否仍用 `data-test` 属性
- 浏览器未装 → 重跑 `uv run playwright install chromium`

- [ ] **Step 9.5: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add tests/auth/
git commit -m "feat(tests): add auth tests (login valid/invalid/logout)"
```

---

## Task 10: Inventory 测试 —— conftest + 3 个测试

**Files:**
- Create: `tests/inventory/__init__.py`(空)
- Create: `tests/inventory/conftest.py`
- Create: `tests/inventory/test_inventory.py`(3 个测试)

**Interfaces:**
- Produces fixture `inventory`(function) → `InventoryPage`,已登录状态
- Produces 3 个测试:
  - `test_inventory_loads_after_login` —— 默认显示 6 件商品
  - `test_sort_by_price_low_to_high` —— 排序后第一件价格最低
  - `test_add_to_cart_updates_badge` —— 加入购物车后徽标 = "1"

- [ ] **Step 10.1: 创建 `tests/inventory/__init__.py`**

```bash
cd F:/project/git/playwright-auto-test
echo. > tests/inventory/__init__.py
```

- [ ] **Step 10.2: 创建 `tests/inventory/conftest.py`**

写入完整内容:

```python
"""Inventory-domain conftest: provides an InventoryPage after login."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage


@pytest.fixture
def inventory(logged_in_page: Page) -> InventoryPage:
    """Return an InventoryPage instance bound to a logged-in page."""
    return InventoryPage(logged_in_page)
```

- [ ] **Step 10.3: 创建 `tests/inventory/test_inventory.py`**

写入完整内容:

```python
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
```

- [ ] **Step 10.4: 运行 inventory 测试套件**

```bash
cd F:/project/git/playwright-auto-test
uv run pytest tests/inventory/ -v
```

预期:3 个测试全部 PASS。

- [ ] **Step 10.5: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add tests/inventory/
git commit -m "feat(tests): add inventory tests (load/sort/add-to-cart)"
```

---

## Task 11: Cart 测试 —— 2 个测试

**Files:**
- Create: `tests/cart/__init__.py`(空)
- Create: `tests/cart/test_cart.py`(2 个测试,无专属 conftest)

**Interfaces:**
- Produces 2 个测试:
  - `test_add_then_remove_item_from_cart` —— 加入再移除,购物车为空
  - `test_cart_persists_items_across_pages` —— 加入商品后跳到 cart 仍可见

- [ ] **Step 11.1: 创建 `tests/cart/__init__.py`**

```bash
cd F:/project/git/playwright-auto-test
echo. > tests/cart/__init__.py
```

- [ ] **Step 11.2: 创建 `tests/cart/test_cart.py`**

写入完整内容:

```python
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
    remove_buttons = inventory_back.page.locator('button[data-test^="remove"]')
    assert remove_buttons.count() == 2
```

- [ ] **Step 11.3: 运行 cart 测试套件**

```bash
cd F:/project/git/playwright-auto-test
uv run pytest tests/cart/ -v
```

预期:2 个测试全部 PASS。

- [ ] **Step 11.4: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add tests/cart/
git commit -m "feat(tests): add cart tests (add/remove + cross-page persistence)"
```

---

## Task 12: 全套测试 + Allure 验证

**Files:** 无新文件

**Interfaces:**
- 验证:`reports/allure-results/` 含测试结果文件
- 验证:`uv run pytest` 8 个测试全 PASS

- [ ] **Step 12.1: 清理旧报告并跑全量测试**

```bash
cd F:/project/git/playwright-auto-test
rm -rf reports/allure-results test-results
uv run pytest
```

Windows 等价:`Remove-Item -Recurse -Force reports/allure-results,test-results`(PowerShell)
或 `rmdir /S /Q reports\allure-results test-results`(cmd)。

预期:输出 `8 passed in <Xs>`,无失败。

- [ ] **Step 12.2: 验证 Allure 原始数据已生成**

```bash
cd F:/project/git/playwright-auto-test
ls reports/allure-results/ | head -20
```

预期:看到若干 `-result.json` 文件(每个测试一个)。若为空,说明 `--alluredir` 配置未生效,回查 `pyproject.toml` 的 `[tool.pytest.ini_options]`。

- [ ] **Step 12.3: 验证 pytest-playwright 失败产物目录(此处无失败,目录可能不存在)**

```bash
cd F:/project/git/playwright-auto-test
ls test-results/ 2>&1 || echo "OK: no failures, test-results not created"
```

预期:`OK: no failures, test-results not created`(全部通过时不创建)。

- [ ] **Step 12.4: 强制触发一次失败以验证 trace/screenshot 产物**

临时修改 `tests/auth/test_login.py` 中的 `test_login_with_invalid_credentials`,把期望文本改成 `definitely_not_present_xyz`:

```python
login_page.expect_error("definitely_not_present_xyz")
```

跑测试:

```bash
cd F:/project/git/playwright-auto-test
uv run pytest tests/auth/test_login.py::test_login_with_invalid_credentials -v
```

预期:测试 FAIL。然后检查:

```bash
cd F:/project/git/playwright-auto-test
ls test-results/
find test-results -name "*.zip" -o -name "*.png" | head
```

预期:看到 `test-login-with-invalid-credentials-*` 子目录,内含 `.zip` (trace) 和 `.png` (screenshot) 文件。

- [ ] **Step 12.5: 还原测试代码并重跑确认恢复**

```bash
cd F:/project/git/playwright-auto-test
# 把 expect_error("definitely_not_present_xyz") 改回 expect_error("do not match")
uv run pytest tests/auth/test_login.py::test_login_with_invalid_credentials -v
```

预期:测试 PASS。

- [ ] **Step 12.6: 清理失败产物**

```bash
cd F:/project/git/playwright-auto-test
rm -rf test-results reports/allure-results
```

Windows 等价:`rmdir /S /Q test-results reports\allure-results`。

- [ ] **Step 12.7: Commit(确认代码无变化)**

```bash
cd F:/project/git/playwright-auto-test
git status
```

预期:`nothing to commit, working tree clean`。如有任何意外改动,审视后再 commit。

---

## Task 13: 并行执行验证

**Files:** 无新文件

- [ ] **Step 13.1: 用 2 个 worker 跑全量测试**

```bash
cd F:/project/git/playwright-auto-test
uv run pytest -n=2
```

预期:输出 `8 passed in <Xs>`,且每个测试耗时比串行明显缩短(若机器 < 2 核则差别不大,但不应失败)。

- [ ] **Step 13.2: 用 auto workers 跑全量测试**

```bash
cd F:/project/git/playwright-auto-test
uv run pytest
```

预期:8 passed。xdist 默认 `workers=auto` 已配置在 `addopts`。

- [ ] **Step 13.3: 确认无 race condition**

观察两次运行的测试结果一致;若有偶发失败,检查 `--dist=loadfile` 是否生效、是否有共享全局可变状态。

- [ ] **Step 13.4: Commit(无代码变化,跳过)**

如无变化,不需 commit。

---

## Task 14: Jenkinsfile

**Files:**
- Create: `Jenkinsfile`

**Interfaces:**
- 6 个 stage:Checkout → Setup → Install Browsers → Test → Report → Archive
- 参数化 `HEADLESS`(默认 true)

- [ ] **Step 14.1: 创建 `Jenkinsfile`**

写入完整内容:

```groovy
pipeline {
    agent any

    parameters {
        booleanParam(name: 'HEADLESS', defaultValue: true, description: 'Run browser headless')
    }

    environment {
        HEADLESS = "${params.HEADLESS}"
        ALLURE_RESULTS_DIR = 'reports/allure-results'
    }

    options {
        timestamps()
        ansiColor('xterm')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                sh 'pip install uv'
                sh 'uv sync --all-extras'
            }
        }

        stage('Install Browsers') {
            steps {
                sh 'uv run playwright install --with-deps chromium'
            }
        }

        stage('Test') {
            steps {
                sh 'uv run pytest'
            }
        }

        stage('Report') {
            steps {
                sh 'uv run allure generate reports/allure-results -o reports/allure-report --clean'
            }
        }

    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**, test-results/**', allowEmptyArchive: true
        }
        failure {
            echo 'Tests failed. See archived reports/ and test-results/ for diagnostics.'
        }
    }
}
```

注意:`uv run allure` 需要在镜像里安装 Allure CLI。如果 Jenkins agent 没有,改用 Docker 镜像或单独步骤安装:
```groovy
sh 'pip install allure-pytest'  # 仅提供 Python 绑定
# 生成 HTML 需要 Allure CLI:
sh 'wget -q https://github.com/allure-framework/allure2/releases/download/2.30.0/allure-2.30.0.tgz && tar -xzf allure-2.30.0.tgz && export PATH=$PATH:$PWD/allure-2.30.0/bin'
```
按团队 Jenkins agent 配置选择。

- [ ] **Step 14.2: 验证 Jenkinsfile 语法(本地)**

Jenkinsfile 没有本地语法校验工具,只能用肉眼审。审阅要点:
- 6 个 stage 都齐全
- 参数化 `HEADLESS` 默认 true
- `archiveArtifacts` 路径含 `reports/**, test-results/**`
- `always` 块保证无论成败都归档

- [ ] **Step 14.3: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add Jenkinsfile
git commit -m "ci: add Jenkinsfile with 6-stage pipeline and artifact archiving"
```

---

## Task 15: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 15.1: 创建 `README.md`**

写入完整内容:

````markdown
# Playwright + pytest Web Automation Scaffold

A reusable, opinionated scaffold for browser-based UI tests using
[Playwright](https://playwright.dev/python/) and
[pytest](https://docs.pytest.org/).

Designed to be **cloned, adapted, and pointed at your own site**.

## Features

- Playwright + pytest, Chromium only
- Allure reporting with failure screenshots and traces
- pytest-xdist parallel execution (`-n=auto`)
- Page Object Model with `data-test` selector convention
- `pydantic-settings` for `.env`-based config
- Jenkinsfile ready to run
- Example tests against [saucedemo.com](https://www.saucedemo.com)

## Quick Start

```bash
# 1. Clone
git clone <your-repo-url> playwright-auto-test
cd playwright-auto-test

# 2. Install deps + browser
uv sync
uv run playwright install chromium

# 3. Copy env template
cp .env.example .env

# 4. Run all 8 example tests
uv run pytest

# 5. Open Allure report
uv run allure serve reports/allure-results
```

## Directory Layout

```
.
├── pages/                # Page Object Model (BasePage + concrete pages)
├── utils/                # Cross-cutting helpers (config, helpers)
├── tests/
│   ├── conftest.py       # Global fixtures (settings, credentials)
│   ├── auth/             # Login tests + conftest
│   ├── inventory/        # Inventory tests + conftest
│   └── cart/             # Cart tests
├── reports/              # Allure output (gitignored)
├── test-results/         # Playwright trace/screenshots on failure (gitignored)
├── pyproject.toml        # Project metadata + deps + pytest config
├── Jenkinsfile           # 6-stage CI pipeline
└── .env.example          # Template for local .env
```

## Adapting to Your Own Site

1. **Update `.env`** — change `BASE_URL`, `SAUCE_USERNAME`, `SAUCE_PASSWORD`.
2. **Rewrite page objects** in `pages/` — replace Sauce Demo selectors with yours.
3. **Rewrite example tests** in `tests/` to match your business flows.
4. **Add new test directories** following the `tests/<domain>/{conftest.py,test_*.py}` pattern.

## Common Commands

```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/auth/test_login.py -v

# Run tests by marker
uv run pytest -m smoke
uv run pytest -m regression

# Run with explicit worker count
uv run pytest -n=4

# Open the Allure HTML report
uv run allure serve reports/allure-results

# Lint
uv run ruff check .
uv run ruff format .
```

## Troubleshooting

| Issue | Fix |
|---|---|
| `Executable doesn't exist` | `uv run playwright install chromium` |
| Tests fail to find elements | Verify your site still exposes `data-test` attributes; if not, update selectors in `pages/` |
| Allure command not found | Install [Allure CLI](https://allurereport.org/docs/install/) separately |
| Parallel tests flake | Check `--dist=loadfile` is in `addopts`; do not share mutable state across tests |

## Tech Stack

| Component | Choice |
|---|---|
| Python | 3.12 |
| Dependency manager | uv |
| Browser | Chromium (Playwright) |
| Test framework | pytest + pytest-playwright + pytest-xdist |
| Reporting | Allure (allure-pytest) |
| Config | pydantic-settings + python-dotenv |
| Lint | ruff |

## License

Pick a license (MIT/Apache-2.0) before publishing.
````

- [ ] **Step 15.2: 验证 README 渲染**

```bash
cd F:/project/git/playwright-auto-test
head -30 README.md
```

预期:看到项目标题与 quick start 部分,Markdown 格式正确。

- [ ] **Step 15.3: Commit**

```bash
cd F:/project/git/playwright-auto-test
git add README.md
git commit -m "docs: add comprehensive README with quickstart and adaptation guide"
```

---

## Task 16: 最终验收

**Files:** 无新文件

- [ ] **Step 16.1: 干净环境再走一遍 quick start**

模拟新克隆机器:

```bash
cd F:/project/git/playwright-auto-test
uv sync
uv run playwright install chromium
uv run pytest
```

预期:8 个测试全部 PASS,无预先存在的报告目录(`.gitignore` 已排除)。

- [ ] **Step 16.2: 验收标准(对应 spec §16)**

| # | 验收项 | 命令 | 期望 |
|---|---|---|---|
| 1 | 干净机器一次成功 | Task 16.1 | 8 passed |
| 2 | `uv run pytest` 全通过 | `uv run pytest` | 8 passed |
| 3 | Allure 报告生成 | `ls reports/allure-results/` | 多个 `-result.json` |
| 4 | 并行执行 | `uv run pytest -n=2` | 8 passed |
| 5 | Jenkinsfile 完整 | `cat Jenkinsfile` | 6 stages |
| 6 | README 步骤清晰 | 阅读 README | 涵盖 quick start |

- [ ] **Step 16.3: 清理工作目录**

```bash
cd F:/project/git/playwright-auto-test
rm -rf reports/allure-results test-results
```

Windows 等价:`rmdir /S /Q reports\allure-results test-results`。

- [ ] **Step 16.4: 最终 commit(若 spec/plan 有更新)**

```bash
cd F:/project/git/playwright-auto-test
git status
git log --oneline
```

预期:工作树干净,git log 展示完整任务序列。

---

## Self-Review Checklist(写完后执行)

- [ ] **Spec 覆盖**:6 大功能区(架构、POM、fixture、配置、CI、文档)是否都有对应 task?—— ✅ Task 1-15 覆盖
- [ ] **占位符扫描**:无 TBD/TODO/模糊措辞 —— ✅
- [ ] **类型一致性**:fixture 命名 (`logged_in_page` vs `inventory`)、page object 方法签名在 task 间一致 —— ✅
- [ ] **可执行性**:每步有具体命令或代码块 —— ✅

---

## 完成状态

**最终交付:**
- ✅ uv + pyproject.toml 配置完整
- ✅ 3 个页面对象(LoginPage/InventoryPage/CartPage)+ BasePage
- ✅ 3 套层级 conftest
- ✅ 8 个示例测试全通过
- ✅ Allure + xdist 可用
- ✅ Jenkinsfile 6-stage
- ✅ README 完整

**预期 commit 序列:**

```
1. chore: bootstrap uv project with deps and ruff config
2. chore: install chromium browser and update uv.lock
3. feat(utils): add pydantic-settings based config loader
4. feat(pages): add BasePage with goto, screenshot, current_url
5. feat(pages): add LoginPage for saucedemo.com
6. feat(pages): add InventoryPage for saucedemo.com
7. feat(pages): add CartPage for saucedemo.com
8. feat(tests): add global conftest with settings/credentials fixtures
9. feat(tests): add auth tests (login valid/invalid/logout)
10. feat(tests): add inventory tests (load/sort/add-to-cart)
11. feat(tests): add cart tests (add/remove + cross-page persistence)
12. ci: add Jenkinsfile with 6-stage pipeline and artifact archiving
13. docs: add comprehensive README with quickstart and adaptation guide
```

外加 Task 12/13/16 的临时 commit 视实际情况而定。
