"""Locator contract for product buttons. No browser."""

from selenium.webdriver.common.by import By

from pages.products import add_button, remove_button


def test_add_and_remove_buttons_use_data_test_selectors() -> None:
    by, selector = add_button("Sauce Labs Backpack")
    assert by == By.CSS_SELECTOR
    assert selector == "[data-test='add-to-cart-sauce-labs-backpack']"

    _by, selector = remove_button("Sauce Labs Bike Light")
    assert selector == "[data-test='remove-sauce-labs-bike-light']"


def test_slug_keeps_punctuation_used_by_saucedemo() -> None:
    _by, selector = add_button("Test.allTheThings() T-Shirt (Red)")
    assert selector == "[data-test='add-to-cart-test.allthethings()-t-shirt-(red)']"
