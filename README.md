# SauceDemo UI automation

[![UI tests](https://github.com/Potucky/Autotest-15may/actions/workflows/ui-tests.yml/badge.svg)](https://github.com/Potucky/Autotest-15may/actions/workflows/ui-tests.yml)

Selenium + pytest UI framework for the public [SauceDemo](https://www.saucedemo.com) store. It uses the Page Object Model, explicit waits, and a checkout check that reconciles line prices, tax, and the order total.

This is a personal portfolio demo for QA Automation, SDET, and Data QA roles. It is not employer code and it is not a production suite.

The badge follows the default branch of `Potucky/Autotest-15may`. If the repository is renamed, update the badge URL in this file.

## What it demonstrates

- Page objects for login, inventory, cart, and checkout
- Login with a valid user, a bad password, missing fields, and the locked-out user
- Logout, including a check that the inventory URL is no longer available
- Sorting by name and by price
- Cart badge, line items, and removal
- Checkout validation, then a completed order whose subtotal, 8% tax, and total agree
- Settings in `config/settings.yaml`, overridden by environment variables
- Headless Chrome in CI, HTML and JUnit reports, and a screenshot on failure

## Tech stack

| Piece | Choice |
| --- | --- |
| Language | Python 3.12 |
| Browser automation | Selenium 4 (Selenium Manager resolves ChromeDriver) |
| Test runner | pytest |
| Reports | pytest-html (self-contained HTML) and pytest JUnit XML |
| Config | YAML plus `BASE_URL`, `BROWSER`, `HEADLESS`, `TIMEOUT` |
| CI | GitHub Actions, headless Chrome on `ubuntu-latest` |

## Project structure

```
config/settings.yaml          default base URL, browser, headless, timeout
framework/                    settings, Chrome driver, price parsing, demo users
pages/                        page objects
tests/                        UI scenarios plus fast checks for config, prices, locators
.github/workflows/ui-tests.yml
reports/                      generated HTML and JUnit XML (not committed)
screenshots/                  PNG saved when a test fails (not committed)
```

## Run locally

Python 3.12 and Google Chrome are required. ChromeDriver is downloaded by Selenium Manager on the first run.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```

There is no display on a CI runner or a remote shell, so turn headless mode on:

```bash
HEADLESS=true python -m pytest
```

Useful subsets:

```bash
python -m pytest -m smoke       # valid login and the full checkout
python -m pytest -m "not ui"    # config, price, and locator checks only
python -m pytest tests/test_login.py
```

A full local run is well under a minute. One headless run of this suite finished in about 10 seconds with 31 passed.

## Configuration

`config/settings.yaml` holds the defaults. Environment variables override the file.

| Variable | Default | Purpose |
| --- | --- | --- |
| `BASE_URL` | `https://www.saucedemo.com` | Site under test |
| `BROWSER` | `chrome` | Only Chrome is supported |
| `HEADLESS` | `false` | `true` or `false`. CI sets `true` |
| `TIMEOUT` | `15` | Explicit-wait timeout in seconds |

Implicit waits are left at 0. Tests wait for a visible element, a URL, or a cart badge.

## Reports

`python -m pytest` writes:

- `reports/report.html` — self-contained HTML report
- `reports/junit.xml` — JUnit XML

Open the HTML file in a browser. The environment block shows the base URL, browser, and headless flag. When a test fails during the test body, the report embeds a screenshot and the same PNG is saved under `screenshots/`. The sample below is a passing run, so the Links column is empty.

## Sample output

```text
$ HEADLESS=true python -m pytest
...............................                                          [100%]
31 passed in 10.23s
```

![HTML report for a passing SauceDemo run](docs/sample-report.png)

## Test approach

Each UI test gets its own browser, so cookies and cart contents do not leak between tests. Page objects own locators and actions. Tests own the assertions.

Waits are `WebDriverWait` checks: the inventory list has reordered, the Remove button has replaced Add to cart, the cart badge shows the expected count, or the URL has changed. There is no `time.sleep`.

Two SauceDemo behaviors in headless Chrome are handled on purpose:

- A WebDriver pointer click on the menu button opens the menu and closes it again in the same gesture, and some inventory buttons ignore the hit. `BasePage.click` fires the DOM click event React listens for, then the test waits until the screen actually changes.
- `element.clear()` desynchronizes the checkout form, so later keystrokes never appear. `BasePage.fill` sets the input the way React expects and waits until the field shows that value.

Prices use `Decimal`, not floats. SauceDemo tax is 8% of the item total, rounded half up to the cent. The checkout test reads the prices on the inventory cards, checks those same amounts on the overview, and checks that tax and total follow that rule. For the backpack (`$29.99`) and bike light (`$9.99`) that is a `$39.98` subtotal, `$3.20` tax, and a `$43.18` total.

## Scenario coverage

Covered against the live demo site:

- Valid login, unknown user, missing username, missing password, locked-out user, logout
- Default name order, Z-to-A, back to A-to-Z, price low-to-high, price high-to-low
- Add one item (badge), add two items (order and prices), remove one
- Checkout with an empty form, and a purchase whose money adds up

Not covered, on purpose for a small demo:

- `problem_user`, `performance_glitch_user`, `error_user`, and `visual_user`
- Other browsers, mobile viewports, and visual regression
- API calls or network stubs. Every UI test uses the public site

The fast tests (no browser) cover the settings loader, the price parser, the tax rounding, and the `data-test` slugs, including `Test.allTheThings() T-Shirt (Red)`.

## Continuous integration

`.github/workflows/ui-tests.yml` runs on pushes to `main`, on pull requests into `main`, and on manual dispatch. The job installs the pinned requirements, runs `python -m pytest` with `HEADLESS=true`, and always uploads `reports/` and `screenshots/` as the `test-report` artifact (kept for 14 days).

## Demo accounts

SauceDemo prints these accounts on its login page. They are public demo credentials, not secrets, and nothing else is stored in this repo.

| User | Password | Used for |
| --- | --- | --- |
| `standard_user` | `secret_sauce` | The scenarios that sign in |
| `locked_out_user` | `secret_sauce` | The locked-account error |

## Author

Vasyl Popovich · [Potucky](https://github.com/Potucky)
