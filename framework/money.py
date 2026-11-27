"""Parse on-screen prices and the SauceDemo tax rule."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

TAX_RATE = Decimal("0.08")
CENTS = Decimal("0.01")


def parse_price(text: str) -> Decimal:
    """Return the amount in labels such as '$29.99' or 'Tax: $3.20'."""
    if "$" not in text:
        raise ValueError(f"Could not parse a price from {text!r}.")
    amount = text.rsplit("$", 1)[-1].strip()
    try:
        return Decimal(amount)
    except InvalidOperation as exc:
        raise ValueError(f"Could not parse a price from {text!r}.") from exc


def expected_tax(subtotal: Decimal) -> Decimal:
    """SauceDemo tax: 8% of the item total, rounded half up to the cent."""
    return (subtotal * TAX_RATE).quantize(CENTS, rounding=ROUND_HALF_UP)
