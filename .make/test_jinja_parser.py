from __future__ import annotations

from pathlib import Path

import pytest
from jinja_parser import get


def _render(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, template: str, **config: str) -> str:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "template.j2"
    source.write_text(template, encoding="utf-8")
    output = tmp_path / "output.html"

    get(template="template.j2", output=str(output), config=dict(config))

    return output.read_text(encoding="utf-8")


def test_get_renders_variables(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = _render(tmp_path, monkeypatch, "Hello {{ name }}!", name="Davide")

    assert rendered == "Hello Davide!"


def test_get_supports_custom_block_delimiters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rendered = _render(tmp_path, monkeypatch, "{! if flag !}yes{! endif !}", flag="1")

    assert rendered == "yes"


def test_get_registers_markdown_filter(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rendered = _render(tmp_path, monkeypatch, '{{ "# Title" | markdown }}')

    assert rendered == "<h1>Title</h1>"
