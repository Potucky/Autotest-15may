"""Shopping cart."""

from __future__ import annotations

from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

from framework.money import parse_price
from pages.base_page import BasePage, Locator
from pages.checkout_page import CheckoutInfoPage
from pages.products import remove_button


class CartPage(BasePage):
    ITEM: Locator = (By.CSS_SELECTOR, ".cart_item")
    ITEM_NAME: Locator = (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
    CHECKOUT: Locator = (By.CSS_SELECTOR, "[data-test='checkout']")

    def wait_until_loaded(self) -> None:
        self.wait.until(EC.url_contains("/cart.html"))
        self.find(self.CHECKOUT)

    def item_names(self) -> list[str]:
        return [element.text.strip() for element in self.driver.find_elements(*self.ITEM_NAME)]

    def price_of(self, product_name: str) -> Decimal:
        for item in self.driver.find_elements(*self.ITEM):
            name = item.find_element(By.CSS_SELECTOR, ".inventory_item_name").text.strip()
            if name == product_name:
                return parse_price(item.find_element(By.CSS_SELECTOR, ".inventory_item_price").text)
        raise LookupError(f"Product not in the cart: {product_name}")

    def remove(self, product_name: str) -> None:
        self.click(remove_button(product_name))

        def _gone(_driver: WebDriver) -> bool:
            return product_name not in self.item_names()

        self.wait.until(_gone, message=f"{product_name!r} was still in the cart.")

    def checkout(self) -> CheckoutInfoPage:
        self.click(self.CHECKOUT)
        page = CheckoutInfoPage(self.driver, self.settings)
        page.wait_until_loaded()
        return page
