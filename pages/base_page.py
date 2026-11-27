"""Shared waits, clicks, and the header cart used by every page."""

from __future__ import annotations

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from framework.config import Settings, load_settings

Locator = tuple[str, str]

# SauceDemo's checkout inputs ignore Selenium clear() + send_keys: clear()
# desynchronizes the React value tracker and the keystrokes never appear.
_SET_INPUT_VALUE = """
const element = arguments[0];
const value = arguments[1];
const prototype = Object.getPrototypeOf(element);
const descriptor = Object.getOwnPropertyDescriptor(prototype, 'value');
descriptor.set.call(element, value);
element.dispatchEvent(new Event('input', { bubbles: true }));
element.dispatchEvent(new Event('change', { bubbles: true }));
"""


class BasePage:
    CART_BADGE: Locator = ("css selector", "[data-test='shopping-cart-badge']")
    CART_LINK: Locator = ("css selector", "[data-test='shopping-cart-link']")

    def __init__(self, driver: WebDriver, settings: Settings | None = None) -> None:
        self.driver = driver
        self.settings = settings or load_settings()
        self.wait = WebDriverWait(
            driver,
            self.settings.timeout,
            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException),
        )

    def find(self, locator: Locator) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def visible_text(self, locator: Locator) -> str:
        return " ".join(self.find(locator).text.split())

    def fill(self, locator: Locator, value: str) -> None:
        """Enter text into a React input and wait until the field shows it."""

        def _attempt(driver: WebDriver) -> bool:
            element = driver.find_element(*locator)
            if not element.is_displayed():
                return False
            try:
                driver.execute_script(_SET_INPUT_VALUE, element, value)
            except StaleElementReferenceException:
                return False
            return element.get_attribute("value") == value

        self.wait.until(_attempt, message=f"Could not enter text into {locator}.")

    def click(self, locator: Locator) -> None:
        """Click once the element is visible.

        Headless Chrome drops WebDriver's pointer click on this site. The menu
        button opens and closes inside one pointer sequence, and inventory
        buttons sometimes ignore the hit. React listens for a click event, so
        this fires that event and the caller waits for the screen to change.
        """

        def _attempt(driver: WebDriver) -> bool:
            element = driver.find_element(*locator)
            if not element.is_displayed() or not element.is_enabled():
                return False
            try:
                driver.execute_script("arguments[0].click();", element)
            except StaleElementReferenceException:
                return False
            return True

        self.wait.until(_attempt, message=f"Could not click {locator}.")

    def cart_count(self) -> int:
        badges = self.driver.find_elements(*self.CART_BADGE)
        if not badges:
            return 0
        text = badges[0].text.strip()
        return int(text) if text else 0

    def wait_for_cart_count(self, expected: int) -> None:
        self.wait.until(
            lambda _driver: self.cart_count() == expected,
            message=f"Shopping cart badge did not become {expected}.",
        )
