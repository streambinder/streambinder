from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

import pytest

from streambinder import minify


class _FakeRun:
    def __init__(self, fail: bool = False) -> None:
        self.calls: list[list[str]] = []
        self.fail = fail

    def __call__(self, cmd: list[str], check: bool) -> subprocess.CompletedProcess[str]:
        self.calls.append(cmd)
        if self.fail:
            raise subprocess.CalledProcessError(1, cmd)
        Path(cmd[-1]).write_text("minified", encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0)


def _tree(tmp_path: Path) -> dict[str, Path]:
    files = {
        "html": tmp_path / "index.html",
        "css": tmp_path / "css" / "main.css",
        "js": tmp_path / "app.js",
        "txt": tmp_path / "notes.txt",
    }
    files["css"].parent.mkdir()
    for path in files.values():
        path.write_text("original", encoding="utf-8")
    return files


def test_main_minifies_known_extensions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    files = _tree(tmp_path)
    fake = _FakeRun()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setenv("BUILD_DIR", str(tmp_path))

    minify.main()

    assert len(fake.calls) == 3
    html_call = next(c for c in fake.calls if any(p.endswith(".html") for p in c))
    assert "--html-keep-quotes" in html_call
    css_call = next(c for c in fake.calls if any(p.endswith(".css") for p in c))
    assert "--html-keep-quotes" not in css_call
    assert files["html"].read_text(encoding="utf-8") == "minified"
    assert files["css"].read_text(encoding="utf-8") == "minified"
    assert files["js"].read_text(encoding="utf-8") == "minified"
    assert files["txt"].read_text(encoding="utf-8") == "original"


def test_minify_failure_propagates_and_keeps_original(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    files = _tree(tmp_path)
    fake = _FakeRun(fail=True)
    monkeypatch.setattr(subprocess, "run", fake)

    with pytest.raises(subprocess.CalledProcessError):
        minify.minify_file(files["html"])

    assert files["html"].read_text(encoding="utf-8") == "original"


def test_module_runs_as_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _tree(tmp_path)
    fake = _FakeRun()
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setenv("BUILD_DIR", str(tmp_path))

    runpy.run_module("streambinder.minify", run_name="__main__")

    assert len(fake.calls) == 3
