"""Name and price sorting on the inventory."""

import pytest

from pages.inventory_page import InventoryPage
from tests.catalog import HIGHEST_PRICE, LOWEST_PRICE

pytestmark = [pytest.mark.ui, pytest.mark.inventory]


def test_products_default_to_name_ascending(inventory_page: InventoryPage) -> None:
    names = inventory_page.product_names()
    assert len(names) >= 2
    assert names == sorted(names)
    assert names[0] == "Sauce Labs Backpack"


def test_sort_by_name_descending(inventory_page: InventoryPage) -> None:
    original = inventory_page.product_names()
    expected = list(reversed(original))
    assert original != expected

    inventory_page.sort_by("za")
    names = inventory_page.wait_until_product_names(expected)
    assert names == sorted(original, reverse=True)


def test_sort_by_name_ascending_after_descending(inventory_page: InventoryPage) -> None:
    original = inventory_page.product_names()
    inventory_page.sort_by("za")
    inventory_page.wait_until_product_names(list(reversed(original)))

    inventory_page.sort_by("az")
    names = inventory_page.wait_until_product_names(original)
    assert names == sorted(original)


@pytest.mark.parametrize(
    ("value", "descending", "first", "last"),
    [
        ("lohi", False, LOWEST_PRICE, HIGHEST_PRICE),
        ("hilo", True, HIGHEST_PRICE, LOWEST_PRICE),
    ],
    ids=["price-low-to-high", "price-high-to-low"],
)
def test_sort_by_price(inventory_page: InventoryPage, value: str, descending: bool, first, last) -> None:
    original = inventory_page.product_prices()
    expected = sorted(original, reverse=descending)
    assert original != expected

    inventory_page.sort_by(value)
    prices = inventory_page.wait_until_prices(expected)
    assert prices[0] == first
    assert prices[-1] == last
