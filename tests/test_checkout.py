"""Checkout validation and a price, tax, and total reconciliation."""

import pytest

from framework.money import expected_tax
from pages.inventory_page import InventoryPage
from tests.catalog import BACKPACK, BIKE_LIGHT

pytestmark = [pytest.mark.ui, pytest.mark.checkout]

THANK_YOU = "Thank you for your order!"
DISPATCHED = (
    "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
)


@pytest.mark.smoke
def test_checkout_reconciles_line_prices_tax_and_total(inventory_page: InventoryPage) -> None:
    backpack = inventory_page.price_of(BACKPACK)
    light = inventory_page.price_of(BIKE_LIGHT)
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.add_to_cart(BIKE_LIGHT)

    overview = inventory_page.open_cart().checkout().continue_with("Alex", "Morgan", "10001")

    assert overview.item_names() == [BACKPACK, BIKE_LIGHT]
    assert overview.item_prices() == [backpack, light]
    assert overview.subtotal() == backpack + light
    assert overview.tax() == expected_tax(overview.subtotal())
    assert overview.total() == overview.subtotal() + overview.tax()
    assert overview.payment_information() == "SauceCard #31337"
    assert overview.shipping_information() == "Free Pony Express Delivery!"

    confirmation = overview.finish()
    assert confirmation.header() == THANK_YOU
    assert confirmation.message() == DISPATCHED


def test_checkout_requires_a_first_name(inventory_page: InventoryPage) -> None:
    inventory_page.add_to_cart(BACKPACK)
    info = inventory_page.open_cart().checkout()
    info.submit()
    assert info.error_message() == "Error: First Name is required"
