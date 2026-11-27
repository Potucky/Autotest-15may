"""Locators for SauceDemo add and remove buttons."""

from __future__ import annotations

from selenium.webdriver.common.by import By

Locator = tuple[str, str]


def slug(product_name: str) -> str:
    """Match the slug SauceDemo puts in data-test attributes."""
    return product_name.lower().replace(" ", "-")


def add_button(product_name: str) -> Locator:
    return (By.CSS_SELECTOR, f"[data-test='add-to-cart-{slug(product_name)}']")


def remove_button(product_name: str) -> Locator:
    return (By.CSS_SELECTOR, f"[data-test='remove-{slug(product_name)}']")
