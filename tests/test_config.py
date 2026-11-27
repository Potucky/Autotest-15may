"""Settings file and environment overrides. These tests do not open a browser."""

from __future__ import annotations

from pathlib import Path

import pytest

from framework.config import Settings, load_settings
from framework.driver_factory import create_driver


def _write_settings(path: Path, browser: str = "chrome", headless: str = "false", timeout: int = 5) -> Path:
    path.write_text(
        "\n".join(
            [
                "base_url: https://example.test/demo",
                f"browser: {browser}",
                f"headless: {headless}",
                f"timeout: {timeout}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_yaml_file_is_read(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("BASE_URL", "BROWSER", "HEADLESS", "TIMEOUT"):
        monkeypatch.delenv(name, raising=False)
    settings = load_settings(_write_settings(tmp_path / "settings.yaml", headless="true", timeout=4))
    assert settings == Settings(
        base_url="https://example.test/demo",
        browser="chrome",
        headless=True,
        timeout=4,
    )


def test_environment_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BASE_URL", "https://override.test/")
    monkeypatch.setenv("BROWSER", "Chrome")
    monkeypatch.setenv("HEADLESS", "yes")
    monkeypatch.setenv("TIMEOUT", "12")
    settings = load_settings(_write_settings(tmp_path / "settings.yaml"))
    assert settings == Settings(
        base_url="https://override.test",
        browser="chrome",
        headless=True,
        timeout=12,
    )


def test_repository_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("BASE_URL", "BROWSER", "HEADLESS", "TIMEOUT"):
        monkeypatch.delenv(name, raising=False)
    assert load_settings() == Settings(
        base_url="https://www.saucedemo.com",
        browser="chrome",
        headless=False,
        timeout=15,
    )


@pytest.mark.parametrize("value", ["sometimes", ""])
def test_invalid_headless_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.delenv("HEADLESS", raising=False)
    config = _write_settings(tmp_path / "settings.yaml", headless=value)
    with pytest.raises(ValueError, match="headless"):
        load_settings(config)


def test_invalid_timeout_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TIMEOUT", "fast")
    with pytest.raises(ValueError, match="TIMEOUT"):
        load_settings(_write_settings(tmp_path / "settings.yaml"))


def test_unknown_browser_is_rejected_before_launch() -> None:
    settings = Settings(
        base_url="https://www.saucedemo.com",
        browser="firefox",
        headless=True,
        timeout=5,
    )
    with pytest.raises(ValueError, match="Chrome"):
        create_driver(settings)
