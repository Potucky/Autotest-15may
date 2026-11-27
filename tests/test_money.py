"""Price parsing and the SauceDemo tax rule. No browser."""

from decimal import Decimal

import pytest

from framework.money import expected_tax, parse_price


@pytest.mark.parametrize(
    ("raw", "amount"),
    [
        ("$29.99", Decimal("29.99")),
        ("Item total: $39.98", Decimal("39.98")),
        ("Tax: $3.20", Decimal("3.20")),
        ("Total: $43.18", Decimal("43.18")),
    ],
)
def test_parse_price(raw: str, amount: Decimal) -> None:
    assert parse_price(raw) == amount


def test_parse_price_requires_a_dollar_amount() -> None:
    with pytest.raises(ValueError):
        parse_price("Free")


def test_tax_is_eight_percent_rounded_half_up() -> None:
    subtotal = Decimal("29.99") + Decimal("9.99")
    assert subtotal == Decimal("39.98")
    assert expected_tax(subtotal) == Decimal("3.20")
    assert subtotal + expected_tax(subtotal) == Decimal("43.18")


def test_half_cent_tax_rounds_half_up() -> None:
    # 10.06 * 0.08 = 0.8048, which rounds half up to 0.80.
    assert expected_tax(Decimal("10.06")) == Decimal("0.80")
    # 10.0625 * 0.08 = 0.805, which rounds half up to 0.81.
    assert expected_tax(Decimal("10.0625")) == Decimal("0.81")
