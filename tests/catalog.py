"""Products the UI tests buy or assert against.

Prices are the ones SauceDemo prints on the inventory cards.
"""

from decimal import Decimal

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"

PUBLISHED_PRICES = {
    BACKPACK: Decimal("29.99"),
    BIKE_LIGHT: Decimal("9.99"),
}

LOWEST_PRICE = Decimal("7.99")
HIGHEST_PRICE = Decimal("49.99")
