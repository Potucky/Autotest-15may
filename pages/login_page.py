"""SauceDemo login page."""

from __future__ import annotations

from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator


class LoginPage(BasePage):
    USERNAME: Locator = (By.CSS_SELECTOR, "[data-test='username']")
    PASSWORD: Locator = (By.CSS_SELECTOR, "[data-test='password']")
    LOGIN_BUTTON: Locator = (By.CSS_SELECTOR, "[data-test='login-button']")
    ERROR: Locator = (By.CSS_SELECTOR, "[data-test='error']")

    def open(self) -> None:
        self.driver.get(f"{self.settings.base_url}/")
        self.wait_until_ready()

    def wait_until_ready(self) -> None:
        self.find(self.LOGIN_BUTTON)

    def login(self, username: str, password: str) -> None:
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)

    def login_as(self, username: str, password: str) -> InventoryPage:
        from pages.inventory_page import InventoryPage

        self.login(username, password)
        inventory = InventoryPage(self.driver, self.settings)
        inventory.wait_until_loaded()
        return inventory

    def error_message(self) -> str:
        return self.visible_text(self.ERROR)
