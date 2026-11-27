"""Product inventory: sorting, add-to-cart, and logout."""

from __future__ import annotations

from decimal import Decimal

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from framework.money import parse_price
from pages.base_page import BasePage, Locator
from pages.cart_page import CartPage
from pages.products import add_button, remove_button


class InventoryPage(BasePage):
    TITLE: Locator = (By.CSS_SELECTOR, "[data-test='title']")
    SORT: Locator = (By.CSS_SELECTOR, "[data-test='product-sort-container']")
    ITEM: Locator = (By.CSS_SELECTOR, ".inventory_item")
    PRODUCT_NAME: Locator = (By.CSS_SELECTOR, ".inventory_item_name")
    PRODUCT_PRICE: Locator = (By.CSS_SELECTOR, ".inventory_item_price")
    MENU: Locator = (By.ID, "react-burger-menu-btn")
    LOGOUT: Locator = (By.CSS_SELECTOR, "[data-test='logout-sidebar-link']")

    def wait_until_loaded(self) -> None:
        self.wait.until(EC.url_contains("/inventory.html"))
        self.find(self.TITLE)
        self.wait.until(
            lambda _driver: len(self.product_names()) >= 1,
            message="Inventory did not list any products.",
        )

    def title(self) -> str:
        return self.visible_text(self.TITLE)

    def product_names(self) -> list[str]:
        return [
            element.text.strip()
            for element in self.driver.find_elements(*self.PRODUCT_NAME)
        ]

    def product_prices(self) -> list[Decimal]:
        return [
            parse_price(element.text)
            for element in self.driver.find_elements(*self.PRODUCT_PRICE)
        ]

    def price_of(self, product_name: str) -> Decimal:
        return _price_of(self._item(product_name))

    def sort_by(self, value: str) -> None:
        dropdown = self.wait.until(EC.element_to_be_clickable(self.SORT))
        Select(dropdown).select_by_value(value)
        self.wait.until(
            lambda driver: Select(driver.find_element(*self.SORT)).first_selected_option.get_attribute("value")
            == value,
            message=f"Sort dropdown did not switch to {value!r}.",
        )

    def wait_until_product_names(self, expected: list[str]) -> list[str]:
        def _matches(_driver: WebDriver) -> list[str] | bool:
            names = self.product_names()
            return names if names == expected else False

        return self.wait.until(_matches, message=f"Product names did not become {expected}.")

    def wait_until_prices(self, expected: list[Decimal]) -> list[Decimal]:
        def _matches(_driver: WebDriver) -> list[Decimal] | bool:
            prices = self.product_prices()
            return prices if prices == expected else False

        return self.wait.until(_matches, message=f"Prices did not become {expected}.")

    def add_to_cart(self, product_name: str) -> None:
        self.click(add_button(product_name))
        # The button swaps to Remove only after the item is actually in the cart.
        self.find(remove_button(product_name))

    def open_cart(self) -> CartPage:
        self.click(self.CART_LINK)
        cart = CartPage(self.driver, self.settings)
        cart.wait_until_loaded()
        return cart

    def logout(self) -> LoginPage:
        from pages.login_page import LoginPage

        self.click(self.MENU)
        self.click(self.LOGOUT)
        login = LoginPage(self.driver, self.settings)
        login.wait_until_ready()
        return login

    def _item(self, product_name: str) -> WebElement:
        self.find(self.PRODUCT_NAME)
        for item in self.driver.find_elements(*self.ITEM):
            name = item.find_element(*self.PRODUCT_NAME).text.strip()
            if name == product_name:
                return item
        raise LookupError(f"Product not on the inventory page: {product_name}")


def _price_of(item: WebElement) -> Decimal:
    return parse_price(item.find_element(By.CSS_SELECTOR, ".inventory_item_price").text)
