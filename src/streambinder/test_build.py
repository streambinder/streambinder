from __future__ import annotations

import runpy
from pathlib import Path

import pytest

from streambinder import build, facade, minify, pages, sitemap


def _prepare(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, list[str]]:
    monkeypatch.chdir(tmp_path)
    calls: list[str] = []
    for module, name in (
        (pages, "pages"),
        (facade, "facade"),
        (sitemap, "sitemap"),
        (minify, "minify"),
    ):
        monkeypatch.setattr(module, "main", lambda name=name: calls.append(name))

    build_dir = tmp_path / "build"
    (build_dir / "doc").mkdir(parents=True)
    (build_dir / "doc" / "index.html").write_text("html", encoding="utf-8")
    (build_dir / "doc" / "index.md").write_text("md", encoding="utf-8")
    (build_dir / "doc" / "photo.png").write_text("png", encoding="utf-8")
    (build_dir / "doc" / "_index.html").write_text("fragment", encoding="utf-8")
    (build_dir / "doc" / "_index.yaml").write_text("yaml", encoding="utf-8")
    static = tmp_path / "site" / "static"
    (static / "css").mkdir(parents=True)
    (static / "robots.txt").write_text("robots", encoding="utf-8")
    (static / "css" / "main.css").write_text("css", encoding="utf-8")
    monkeypatch.setenv("BUILD_DIR", str(build_dir))
    return build_dir, calls


def test_main_runs_steps_in_order_and_cleans(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build_dir, calls = _prepare(tmp_path, monkeypatch)

    build.main()

    assert calls == ["pages", "facade", "sitemap", "minify"]
    assert (build_dir / "doc" / "index.html").exists()
    assert (build_dir / "doc" / "index.md").exists()
    assert (build_dir / "doc" / "photo.png").exists()
    assert not (build_dir / "doc" / "_index.html").exists()
    assert not (build_dir / "doc" / "_index.yaml").exists()
    assert (build_dir / "robots.txt").read_text(encoding="utf-8") == "robots"
    assert (build_dir / "css" / "main.css").read_text(encoding="utf-8") == "css"


def test_module_runs_as_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir, calls = _prepare(tmp_path, monkeypatch)

    runpy.run_module("streambinder.build", run_name="__main__")

    assert calls == ["pages", "facade", "sitemap", "minify"]
    assert (build_dir / "robots.txt").exists()
