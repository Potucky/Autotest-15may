"""Checkout information, overview, and confirmation pages."""

from __future__ import annotations

from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from framework.money import parse_price
from pages.base_page import BasePage, Locator


class CheckoutInfoPage(BasePage):
    FIRST_NAME: Locator = (By.CSS_SELECTOR, "[data-test='firstName']")
    LAST_NAME: Locator = (By.CSS_SELECTOR, "[data-test='lastName']")
    POSTAL_CODE: Locator = (By.CSS_SELECTOR, "[data-test='postalCode']")
    CONTINUE: Locator = (By.CSS_SELECTOR, "[data-test='continue']")
    ERROR: Locator = (By.CSS_SELECTOR, "[data-test='error']")

    def wait_until_loaded(self) -> None:
        self.wait.until(EC.url_contains("checkout-step-one.html"))
        self.find(self.FIRST_NAME)

    def submit(self) -> None:
        self.click(self.CONTINUE)

    def continue_with(self, first_name: str, last_name: str, postal_code: str) -> CheckoutOverviewPage:
        self.fill(self.FIRST_NAME, first_name)
        self.fill(self.LAST_NAME, last_name)
        self.fill(self.POSTAL_CODE, postal_code)
        self.submit()
        overview = CheckoutOverviewPage(self.driver, self.settings)
        overview.wait_until_loaded()
        return overview

    def error_message(self) -> str:
        return self.visible_text(self.ERROR)


class CheckoutOverviewPage(BasePage):
    ITEM_NAME: Locator = (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
    ITEM_PRICE: Locator = (By.CSS_SELECTOR, ".cart_item .inventory_item_price")
    PAYMENT: Locator = (By.CSS_SELECTOR, "[data-test='payment-info-value']")
    SHIPPING: Locator = (By.CSS_SELECTOR, "[data-test='shipping-info-value']")
    SUBTOTAL: Locator = (By.CSS_SELECTOR, "[data-test='subtotal-label']")
    TAX: Locator = (By.CSS_SELECTOR, "[data-test='tax-label']")
    TOTAL: Locator = (By.CSS_SELECTOR, "[data-test='total-label']")
    FINISH: Locator = (By.CSS_SELECTOR, "[data-test='finish']")

    def wait_until_loaded(self) -> None:
        self.wait.until(EC.url_contains("checkout-step-two.html"))
        self.find(self.FINISH)

    def item_names(self) -> list[str]:
        return [element.text.strip() for element in self.driver.find_elements(*self.ITEM_NAME)]

    def item_prices(self) -> list[Decimal]:
        return [parse_price(element.text) for element in self.driver.find_elements(*self.ITEM_PRICE)]

    def payment_information(self) -> str:
        return self.visible_text(self.PAYMENT)

    def shipping_information(self) -> str:
        return self.visible_text(self.SHIPPING)

    def subtotal(self) -> Decimal:
        return parse_price(self.visible_text(self.SUBTOTAL))

    def tax(self) -> Decimal:
        return parse_price(self.visible_text(self.TAX))

    def total(self) -> Decimal:
        return parse_price(self.visible_text(self.TOTAL))

    def finish(self) -> CheckoutCompletePage:
        self.click(self.FINISH)
        page = CheckoutCompletePage(self.driver, self.settings)
        page.wait_until_loaded()
        return page


class CheckoutCompletePage(BasePage):
    HEADER: Locator = (By.CSS_SELECTOR, "[data-test='complete-header']")
    TEXT: Locator = (By.CSS_SELECTOR, "[data-test='complete-text']")

    def wait_until_loaded(self) -> None:
        self.wait.until(EC.url_contains("checkout-complete.html"))
        self.find(self.HEADER)

    def header(self) -> str:
        return self.visible_text(self.HEADER)

    def message(self) -> str:
        return self.visible_text(self.TEXT)
