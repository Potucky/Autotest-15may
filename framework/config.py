"""Load project settings from config/settings.yaml and the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS_PATH = ROOT / "config" / "settings.yaml"

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser: str
    headless: bool
    timeout: int


def load_settings(path: Path | None = None) -> Settings:
    """Return settings, with environment variables overriding the YAML file."""
    raw = _read_yaml(path or DEFAULT_SETTINGS_PATH)
    base_url = _text(os.environ.get("BASE_URL", raw.get("base_url", "https://www.saucedemo.com")))
    browser = _text(os.environ.get("BROWSER", raw.get("browser", "chrome"))).lower()
    timeout = _timeout(os.environ.get("TIMEOUT", raw.get("timeout", 15)))
    if "HEADLESS" in os.environ:
        headless = _as_bool(os.environ["HEADLESS"])
    else:
        headless = _as_bool(raw.get("headless", False))

    base_url = base_url.rstrip("/")
    if not base_url.startswith(("http://", "https://")):
        raise ValueError(f"base_url must be an http(s) URL. Got {base_url!r}.")
    if not browser:
        raise ValueError("browser is empty.")
    return Settings(base_url=base_url, browser=browser, headless=headless, timeout=timeout)


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Settings file must be a mapping: {path}")
    return loaded


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _TRUE:
            return True
        if normalized in _FALSE:
            return False
    raise ValueError(f"headless must be true or false. Got {value!r}.")


def _timeout(value: object) -> int:
    try:
        timeout = int(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"TIMEOUT must be a whole number of seconds. Got {value!r}.") from exc
    if timeout <= 0:
        raise ValueError(f"TIMEOUT must be positive. Got {timeout}.")
    return timeout


def _text(value: object) -> str:
    return str(value).strip()
