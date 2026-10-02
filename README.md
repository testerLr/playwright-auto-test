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
