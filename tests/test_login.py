"""Login, rejected credentials, and logout."""

import pytest

from framework.users import LOCKED_OUT_USER, PASSWORD, STANDARD_USER
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.login]

MISMATCH = "Epic sadface: Username and password do not match any user in this service"
LOCKED = "Epic sadface: Sorry, this user has been locked out."
USERNAME_REQUIRED = "Epic sadface: Username is required"
PASSWORD_REQUIRED = "Epic sadface: Password is required"


@pytest.mark.smoke
def test_valid_login_opens_inventory(login_page: LoginPage) -> None:
    inventory = login_page.login_as(STANDARD_USER, PASSWORD)
    assert inventory.driver.current_url.endswith("/inventory.html")
    assert inventory.title() == "Products"
    assert inventory.product_names()


@pytest.mark.parametrize(
    ("username", "password", "message"),
    [
        ("", "", USERNAME_REQUIRED),
        (STANDARD_USER, "", PASSWORD_REQUIRED),
        ("not_a_user", "wrong_password", MISMATCH),
        (LOCKED_OUT_USER, PASSWORD, LOCKED),
    ],
    ids=["missing-username", "missing-password", "unknown-user", "locked-out"],
)
def test_rejected_login(login_page: LoginPage, username: str, password: str, message: str) -> None:
    login_page.login(username, password)
    assert login_page.error_message() == message
    assert "inventory.html" not in login_page.driver.current_url


def test_logout_ends_the_session(inventory_page) -> None:
    login = inventory_page.logout()
    assert login.driver.current_url.rstrip("/") == login.settings.base_url

    login.driver.get(f"{login.settings.base_url}/inventory.html")
    login.wait_until_ready()
    assert "inventory.html" not in login.driver.current_url
