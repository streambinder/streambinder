from __future__ import annotations

import runpy
from pathlib import Path

import facade
import pytest

_WEBSITE_YML = """\
info:
  name: Test Person
  website: https://example.com
  social:
    - name: GitHub
      url: https://example.com/github
pages: []
"""

_TEMPLATE = "Title: {{ html.head.title }} | Body: {{ html.body }} | Info: {{ info.name }}"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / "src" / "website.yml", _WEBSITE_YML)
    _write(tmp_path / "src" / "facade.html.j2", _TEMPLATE)

    build_dir = tmp_path / "build"
    _write(build_dir / "page" / "_index.html", "PAGE BODY")
    _write(build_dir / "page" / "_index.yaml", "html:\n  head:\n    title: Page Title\n")
    _write(build_dir / "page" / "nested" / "_index.html", "NESTED BODY")
    _write(build_dir / "page" / "nested" / "_index.yaml", "html:\n  head:\n    title: Nested\n")
    _write(build_dir / "page" / "index.html", "NOT A FRAGMENT")
    _write(build_dir / "notes.txt", "ignored")
    monkeypatch.setenv("BUILD_DIR", str(build_dir))
    return build_dir


def test_main_wraps_each_fragment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir = _prepare(tmp_path, monkeypatch)

    facade.main()

    page = (build_dir / "page" / "index.html").read_text(encoding="utf-8")
    assert "Title: Page Title" in page
    assert "Body: PAGE BODY" in page
    assert "Info: Test Person" in page
    nested = (build_dir / "page" / "nested" / "index.html").read_text(encoding="utf-8")
    assert "Body: NESTED BODY" in nested


def test_module_runs_as_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir = _prepare(tmp_path, monkeypatch)

    runpy.run_module("facade", run_name="__main__")

    assert (build_dir / "page" / "index.html").exists()
