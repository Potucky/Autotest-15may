"""Browser fixture, HTML report metadata, and screenshots on failure."""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path

import pytest
import pytest_html.extras
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from framework.config import load_settings
from framework.driver_factory import create_driver
from framework.users import PASSWORD, STANDARD_USER
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


@pytest.fixture
def driver() -> Iterator[WebDriver]:
    browser = create_driver()
    try:
        yield browser
    finally:
        browser.quit()


@pytest.fixture
def login_page(driver: WebDriver) -> LoginPage:
    page = LoginPage(driver)
    page.open()
    return page


@pytest.fixture
def inventory_page(login_page: LoginPage) -> InventoryPage:
    return login_page.login_as(STANDARD_USER, PASSWORD)


def pytest_configure(config: pytest.Config) -> None:
    Path("reports").mkdir(parents=True, exist_ok=True)
    Path("screenshots").mkdir(parents=True, exist_ok=True)


def pytest_metadata(metadata: dict[str, str]) -> None:
    settings = load_settings()
    metadata["Base URL"] = settings.base_url
    metadata["Browser"] = settings.browser
    metadata["Headless"] = "yes" if settings.headless else "no"


def pytest_html_report_title(report: object) -> None:
    report.title = "SauceDemo UI tests"  # type: ignore[attr-defined]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    if report.failed and report.when in {"setup", "call"}:
        _attach_failure_screenshot(item, report)


def _attach_failure_screenshot(item: pytest.Item, report: pytest.TestReport) -> None:
    driver = item.funcargs.get("driver")
    if driver is None:
        return
    path = _screenshot_path(item)
    try:
        driver.save_screenshot(str(path))
        encoded = driver.get_screenshot_as_base64()
    except WebDriverException as exc:
        report.sections.append(("screenshot", f"Could not capture screenshot: {exc}"))
        return
    # pytest-html copies extras while handling the call report.
    if report.when != "call":
        return
    extras = list(getattr(report, "extras", []))
    extras.append(pytest_html.extras.png(encoded, name="Failure screenshot"))
    report.extras = extras


def _screenshot_path(item: pytest.Item) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.nodeid)
    return Path("screenshots") / f"{safe}.png"
