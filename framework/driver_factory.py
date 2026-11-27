"""Create a Chrome WebDriver. Implicit waits stay at zero; pages wait explicitly."""

from __future__ import annotations

import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver

from framework.config import Settings, load_settings


def create_driver(settings: Settings | None = None) -> WebDriver:
    settings = settings or load_settings()
    if settings.browser != "chrome":
        raise ValueError(
            f"Unsupported browser {settings.browser!r}. This project runs Google Chrome."
        )

    options = Options()
    if settings.headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-search-engine-choice-screen")
    # DOMContentLoaded is enough. Element waits cover the nodes the tests use,
    # so a slow image does not hold up navigation.
    options.page_load_strategy = "eager"
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        },
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

    service = Service(log_output=os.devnull)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(0)
    return driver
