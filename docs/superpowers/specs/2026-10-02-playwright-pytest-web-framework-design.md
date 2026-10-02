# Playwright + pytest Web 自动化框架 — 设计文档

**日期**: 2026-10-02
**状态**: 草案 v1
**目标仓库**: `playwright-auto-test`

---

## 1. 概述

构建一个**通用、可复用**的 Playwright + pytest Web 自动化测试脚手架模板。仓库
可直接被 `git clone` 后运行示例测试;使用者在此基础上替换目标站点、补充业务用例
即可投入生产使用。

## 2. 目标与范围

### 2.1 包含

- 完整的目录骨架与样板代码
- 3–5 个针对 [saucedemo.com](https://www.saucedemo.com) 的示例测试,覆盖登录、
  商品列表、购物车
- 一份 `Jenkinsfile`,开箱可跑
- 一份 `README.md`,说明如何复用、扩展、迁移到自有站点

### 2.2 不包含(YAGNI)

- 多浏览器矩阵(只支持 Chromium)
- 移动设备模拟
- 内置 API 测试 helper(仅 UI)
- 数据库 / Mock 服务
- 多语言本地化辅助
- 内置测试管理平台 / UI 调度

## 3. 架构决策

| 决策 | 选择 | 理由 |
|---|---|---|
| 框架定位 | 通用脚手架模板 | 可被多项目复用 |
| 浏览器 | 仅 Chromium | 最轻、最快;需求方显式确认 |
| 报告 | Allure | 行业标准,带趋势/历史/附件 |
| 示例目标 | saucedemo.com | 公开 demo,有标准 `data-test` 选择器 |
| POM | 强制扁平 `pages/` + 层级 conftest | 强制结构,conftest 按业务域就近 |
| 配置 | `pyproject.toml` + `.env` | pytest 静态配置 + 运行时密钥分离 |
| CI | Jenkinsfile | 需求方显式确认 |
| 失败产物 | 截图 + trace.zip | 信息量足够,体积可控 |
| 并行 | pytest-xdist,`workers=auto` | 0 配置提速 |
| Python | 3.12 | 稳定甜点,2028-10 前有支持 |
| 依赖管理 | uv + `pyproject.toml` | 速度快、锁文件、社区主流 |

## 4. 目录结构

```
playwright-auto-test/
├── pyproject.toml            # uv 项目 + pytest 配置 + 依赖
├── uv.lock                   # uv 生成,入库
├── .env.example              # 环境变量模板(入库)
├── .env                      # 实际环境(不入库)
├── .gitignore                # .env、reports/、test-results/、.venv/
├── Jenkinsfile
├── README.md
├── pages/                    # POM — 扁平放在根目录
│   ├── __init__.py
│   ├── base_page.py
│   ├── login_page.py
│   ├── inventory_page.py
│   └── cart_page.py
├── utils/
│   ├── __init__.py
│   ├── config.py             # pydantic-settings
│   └── helpers.py
├── tests/
│   ├── conftest.py           # 全局 fixture
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
├── reports/                  # Allure 原始数据 + HTML 报告
└── test-results/             # pytest-playwright 自动生成:trace/截图(video 关闭)
```

### 4.1 目录分层原则

- `pages/` —— 与业务完全无关的页面对象,只通过传入的 `Page` 操作浏览器
- `utils/` —— 跨页面/跨测试的工具,**不持有 `Page` 状态**
- `tests/` —— pytest 入口,`conftest.py` 按业务域就近
- `reports/` —— Allure 输出,Jenkins 上传 artifact 用
- `test-results/` —— pytest-playwright 自动创建,失败时的 trace/截图落点;
  `.gitignore` 排除,Jenkins 上传 artifact 即可

## 5. 依赖

### 5.1 运行依赖

| 包 | 版本下限 | 用途 |
|---|---|---|
| `playwright` | ≥ 1.40 | 浏览器自动化 |
| `pytest` | ≥ 8.0 | 测试框架 |
| `pytest-playwright` | 最新 | pytest 集成,提供 `page` fixture |
| `pytest-xdist` | 最新 | 并行执行 |
| `allure-pytest` | 最新 | Allure 报告 |
| `pydantic-settings` | ≥ 2.0 | `.env` 加载 + 字段校验 |
| `python-dotenv` | 最新 | 兜底兼容 |

### 5.2 开发依赖

| 包 | 用途 |
|---|---|
| `ruff` | lint + format |
| `mypy` | 类型检查(可选) |
| `pytest` | 自测试 |

### 5.3 Python 目标

`requires-python = ">=3.12,<3.13"`

### 5.4 浏览器二进制

- `uv run playwright install chromium`(仅 Chromium,首次需要)
- 文档提示:`playwright install --with-deps chromium`(Linux CI 需要)

## 6. 页面对象层(POM)

### 6.1 BasePage

[pages/base_page.py](pages/base_page.py) 的最小职责:

```python
class BasePage:
    def __init__(self, page: Page): ...
    def goto(self, path: str = "/") -> None: ...
    def screenshot(self, name: str) -> None: ...   # 自动附加到 Allure
    @property
    def current_url(self) -> str: ...
```

- `goto()` 内部读取 `settings.base_url`,拼接并跳转,统一 `wait_until="load"`
- `screenshot()` 通过 `allure.attach` 上传 PNG

### 6.2 具体页面

所有具体页面对象都实现同一个 `open() -> "Self"` 方法:跳转到自己负责的 URL,
返回 `self` 便于链式调用(`LoginPage(page).open().login(...)`)。

#### LoginPage(saucedemo.com 登录页)

| 元素 | data-test 属性 |
|---|---|
| 用户名输入框 | `[data-test="username"]` |
| 密码输入框 | `[data-test="password"]` |
| 登录按钮 | `[data-test="login-button"]` |
| 错误提示 | `[data-test="error"]` |

业务方法:
- `open() -> "LoginPage"` —— 打开登录页,返回 `self`
- `login(username, password)` —— 输入并点击
- `expect_error(text)` —— 断言错误提示文本

#### InventoryPage(商品列表)

| 元素 | data-test 属性 |
|---|---|
| 标题 | `[data-test="title"]` |
| 列表容器 | `[data-test="inventory-container"]` |
| 商品项 | `.inventory_item` |
| 排序下拉 | `[data-test="product-sort-container"]` |
| 加入购物车按钮 | `button[data-test^="add-to-cart"]` |
| 购物车徽标 | `[data-test="shopping-cart-badge"]` |
| 移除按钮 | `button[data-test^="remove"]` |

业务方法:
- `open() -> "InventoryPage"` —— 打开商品列表,返回 `self`
- `add_item_to_cart(index: int)`
- `remove_item_from_cart(index: int)`
- `sort_by(value: Literal["az","za","lohi","hilo"])`
- `item_count() -> int`
- `cart_badge_count() -> int`

#### CartPage(购物车)

| 元素 | data-test 属性 |
|---|---|
| 商品项 | `.cart_item` |
| 继续购物 | `[data-test="continue-shopping"]` |
| 结账 | `[data-test="checkout"]` |
| 移除按钮 | `button[data-test^="remove"]` |

业务方法:
- `open() -> "CartPage"` —— 打开购物车,返回 `self`
- `remove_item(index: int)`
- `item_count() -> int`
- `continue_shopping()`

### 6.3 Locator 风格

- **统一用 `@property`** 返回新 `Locator`,不缓存
- 选择器优先 `data-test`,其次稳定的 id/class
- 不在页面对象里写 `expect_*` 断言,断言放测试里

## 7. Fixture 与 Conftest 层级

### 7.1 顶层 `tests/conftest.py`

提供:
- `settings`(session 作用域)—— `pydantic-settings` 实例
- `browser_context_args`(session)—— 注入 `BASE_URL`、viewport、locale
- `auth_credentials`(session)—— 从 `.env` 读取用户/密码

### 7.2 业务域 conftest

所有跨域 fixture(`logged_in_page`、`inventory`)实际上都集中在
`tests/conftest.py`,因为 pytest 的 conftest 传播只朝子目录方向,不在兄弟
之间共享 —— 把 `inventory` 放在 `tests/inventory/conftest.py` 会导致
`tests/cart/test_cart.py` 看不见它(同理 `logged_in_page` 在
`tests/auth/conftest.py` 会让 inventory / cart 测试找不到它)。`tests/auth/`
和 `tests/inventory/` 仍保留 `conftest.py` 文件以便将来加入域专属 fixture,
但目前只放说明性注释。

`tests/conftest.py`(全局):
- `logged_in_page` —— 用 `LoginPage` 完成登录,返回登录后的 Playwright `Page`(浏览器页)
- `inventory` —— 返回已登录后构造的 `InventoryPage` 实例(POM 对象),依赖 `logged_in_page`

`tests/cart/` 无专属 conftest,直接复用 `inventory` 添加商品后跳转。

### 7.3 Fixture 级联规则

| Fixture | 作用域 | 依赖 | 返回类型 |
|---|---|---|---|
| `settings` | session | — | `Settings` |
| `page` | function | `pytest-playwright` 内置 | playwright `Page` |
| `logged_in_page` | function | `page`、`auth_credentials` | playwright `Page` |
| `inventory` | function | `logged_in_page` | `InventoryPage`(POM) |

依赖图:
```
settings ─► auth_credentials ─► logged_in_page ─► inventory
                                                  │
page ──────────────────────────────────────────────┘
```

**命名约定**:`*_page` 后缀的 fixture 返回浏览器 Page(Playwright 类型);不带后缀的
fixture(`inventory`)返回 POM 对象。这样在测试里看到 `inventory.add_item_to_cart(0)`
不会误以为是浏览器 API。

## 8. 配置与环境

### 8.1 `.env.example`(入库)

```dotenv
# 示例登录账号(Sauce Demo 公开账号)
SAUCE_USERNAME=standard_user
SAUCE_PASSWORD=secret_sauce

# 站点
BASE_URL=https://www.saucedemo.com

# 浏览器行为
HEADLESS=true
VIEWPORT_WIDTH=1280
VIEWPORT_HEIGHT=720
TIMEOUT_MS=30000

# Allure
ALLURE_RESULTS_DIR=reports/allure-results
```

### 8.2 `utils/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str
    sauce_username: str
    sauce_password: str
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout_ms: int = 30000

settings = Settings()  # 模块级单例
```

> 注意:`allure_results_dir` 不在 `Settings` 里 —— Allure 输出目录由
> `pyproject.toml` 的 `--alluredir=reports/allure-results` 控制,与 Python
> 配置解耦。

### 8.3 `pyproject.toml` 中的 `[tool.pytest.ini_options]`

```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
  "-v",
  "--tb=short",
  "--strict-markers",
  "--alluredir=reports/allure-results",
  "-n=auto",
  "--dist=loadfile",   # xdist 按文件分片,避免同文件 race
]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
  "smoke: 冒烟测试",
  "regression: 回归测试",
]
```

## 9. 失败产物

通过 `pytest-playwright` CLI 选项控制(写在 `[tool.pytest.ini_options]` 的 `addopts`):

- `--screenshot=only-on-failure` —— 失败时截图
- `--tracing=retain-on-failure` —— 失败时生成 `trace.zip`
- 不开启 `--video`(体积过大)

### 9.1 Jenkins 上的归档

Jenkinsfile 把以下路径归档为 build artifact:
- `reports/allure-results/**` —— Allure 原始数据
- `test-results/**` —— Playwright trace/screenshot

## 10. 报告(Allure)

### 10.1 本地查看

```bash
uv run pytest
uv run allure serve reports/allure-results
```

### 10.2 测试注解(在测试中使用)

- `@allure.feature("登录")`
- `@allure.story("成功登录")`
- `@allure.severity(allure.severity_level.CRITICAL)`
- 失败时:截图通过 `BasePage.screenshot()` 附加;trace.zip 由 pytest-playwright
  落到 `test-results/`,Jenkinsfile 用 `archiveArtifacts` 一并归档
- 在 Allure 报告查看 trace:配置 `allure.properties` 启用附件或借助
  `pytest_playwright` 的 `pytest_runtest_makereport` 钩子把 trace 路径写入 Allure 链接

## 11. 并行执行

- `pytest-xdist`,`workers=auto`(CPU 核数)
- `--dist=loadfile`:同文件内测试串行,跨文件并行
  - 保证共享 page object 的测试不会跨 worker 抢同一 page
- 测试**不允许**持有跨测试的全局可变状态

## 12. CI(Jenkins)

### 12.1 `Jenkinsfile`(Declarative Pipeline)

Stages:
1. `Checkout` —— 拉代码
2. `Setup` —— `pip install uv && uv sync`
3. `Install Browsers` —— `uv run playwright install --with-deps chromium`
4. `Test` —— `uv run pytest`
5. `Report` —— `allure generate reports/allure-results -o reports/allure-report --clean`
6. `Archive` —— `archiveArtifacts` 上传 `reports/`

特性:
- 参数化构建:`HEADLESS`(默认 true)—— 控制浏览器是否可见
- 失败时保留 `test-results/`(trace + 截图),便于复现

### 12.2 本地与 CI 一致

CI 与本地使用同一组命令(`uv run pytest`),不引入额外脚本。

## 13. 示例测试

### 13.1 `tests/auth/test_login.py`

- `test_login_with_valid_credentials` —— 登录成功,断言跳转到 inventory
- `test_login_with_invalid_credentials` —— 错误密码,断言错误提示
- `test_logout` —— 登录后从菜单登出,断言回到登录页

### 13.2 `tests/inventory/test_inventory.py`

- `test_inventory_loads_after_login` —— 默认显示 6 件商品(由 fixture `inventory` 提供)
- `test_sort_by_price_low_to_high` —— 排序后第一件价格最低
- `test_add_to_cart_updates_badge` —— 加入购物车后徽标 = 1

### 13.3 `tests/cart/test_cart.py`

- `test_add_then_remove_item_from_cart` —— 加入再移除,购物车为空
- `test_cart_persists_items_across_pages` —— 加入商品后跳到 cart 仍可见

总计 8 个示例测试,全部针对 Sauce Demo 的真实公开账号。

> **注意**:示例测试使用对 saucedemo.com 的脆性硬编码假设(如商品数量 = 6)。
> 迁移到自有站点时,这些测试需要替换为针对实际业务的功能测试,而不是简单
> 修改数值断言。

## 14. 文档

### 14.1 README.md 包含

- 项目简介
- 快速开始(克隆 → uv sync → playwright install → pytest)
- 目录结构图与说明
- 如何迁移到自有站点(替换 BASE_URL、新建页面对象、新建测试)
- 常用命令速查(本地跑、跑指定 marker、并行、Allure 报告)
- 常见问题(浏览器没装、trace 打开方式等)

### 14.2 不写

- 详细 API 参考(每个方法 docstring 已经够了)
- 内部设计哲学长文

## 15. 未来扩展(明确不做)

以下功能**明确不**在本脚手架第一版实现,以保持简洁:

- Firefox / WebKit 支持 —— 切换 `--browser` 即可,但不写示例
- 移动设备模拟 —— 不引入 device descriptor
- API 测试 helper —— 不引入 `requests`/`httpx`
- 测试数据工厂 —— 用 .env 简单够用
- 自定义 Allure 插件 —— 不写
- 性能测试 / Lighthouse —— 完全不沾边

## 16. 验收标准

脚手架完成时,以下事实必须成立:

1. `uv sync && uv run playwright install chromium` 在干净机器上一次成功
2. `uv run pytest` 在本地全部 8 个示例测试通过
3. `uv run allure serve reports/allure-results` 能看到完整报告
4. `uv run pytest -n=2` 并行执行通过
5. Jenkinsfile 在 Jenkins 上能跑完整个 pipeline 并归档报告
6. README 步骤能让一个从未接触过该项目的人 10 分钟内跑通
