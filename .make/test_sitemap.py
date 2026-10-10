from __future__ import annotations

import runpy
from pathlib import Path

import pytest
import sitemap

_WEBSITE_YML = """\
info:
  name: Test Person
  website: https://example.com
pages:
  - path: /
  - path: /404
  - path: /500
  - path: /about
"""

_EXPECTED = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    "  <url><loc>https://example.com/</loc></url>\n"
    "  <url><loc>https://example.com/about</loc></url>\n"
    "</urlset>\n"
)


def _prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    website = tmp_path / "src" / "website.yml"
    website.parent.mkdir(parents=True)
    website.write_text(_WEBSITE_YML, encoding="utf-8")
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    monkeypatch.setenv("BUILD_DIR", str(build_dir))
    return build_dir / "sitemap.xml"


def test_main_excludes_error_pages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = _prepare(tmp_path, monkeypatch)

    sitemap.main()

    assert dest.read_text(encoding="utf-8") == _EXPECTED
    assert sitemap.EXCLUDED_PATHS == {"/404", "/500"}


def test_module_runs_as_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    dest = _prepare(tmp_path, monkeypatch)

    runpy.run_module("sitemap", run_name="__main__")

    assert dest.read_text(encoding="utf-8") == _EXPECTED
