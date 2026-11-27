"""Adding products, the cart badge, and removal."""

import pytest

from pages.inventory_page import InventoryPage
from tests.catalog import BACKPACK, BIKE_LIGHT, PUBLISHED_PRICES

pytestmark = [pytest.mark.ui, pytest.mark.cart]


def test_adding_a_product_updates_the_cart_badge(inventory_page: InventoryPage) -> None:
    assert inventory_page.cart_count() == 0
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.wait_for_cart_count(1)
    assert inventory_page.cart_count() == 1


def test_cart_lists_added_products_and_remove_updates_it(inventory_page: InventoryPage) -> None:
    light_price = inventory_page.price_of(BIKE_LIGHT)
    backpack_price = inventory_page.price_of(BACKPACK)
    assert light_price == PUBLISHED_PRICES[BIKE_LIGHT]
    assert backpack_price == PUBLISHED_PRICES[BACKPACK]

    inventory_page.add_to_cart(BIKE_LIGHT)
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.wait_for_cart_count(2)

    cart = inventory_page.open_cart()
    assert cart.item_names() == [BIKE_LIGHT, BACKPACK]
    assert cart.price_of(BIKE_LIGHT) == light_price
    assert cart.price_of(BACKPACK) == backpack_price

    cart.remove(BIKE_LIGHT)
    cart.wait_for_cart_count(1)
    assert cart.item_names() == [BACKPACK]
