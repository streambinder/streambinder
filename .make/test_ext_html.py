from __future__ import annotations

from ext_html import idfy, title


def test_title_prefixes_page_name() -> None:
    assert title("Resume", "Davide Pucci") == "Resume — Davide Pucci"


def test_title_returns_site_title_when_equal() -> None:
    assert title("Davide Pucci", "Davide Pucci") == "Davide Pucci"


def test_idfy_replaces_spaces_and_lowercases() -> None:
    assert idfy("Hello World") == "hello-world"
    assert idfy("Multiple  Spaces") == "multiple--spaces"


def test_idfy_strips_non_alphanumeric_characters() -> None:
    assert idfy("Foo Bar!") == "foo-bar"
    assert idfy("C++ Guide (2026)") == "c-guide-2026"


def test_idfy_keeps_digits_and_hyphens() -> None:
    assert idfy("already-fine-123") == "already-fine-123"
