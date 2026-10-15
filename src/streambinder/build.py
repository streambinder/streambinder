#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
from pathlib import Path

from streambinder import facade, minify, pages, sitemap

_KEEP_NAMES = {"index.html", "index.md"}
_KEEP_SUFFIXES = {".jpg", ".png", ".gif", ".svg"}


def _clean(build_dir: Path) -> None:
    """drop generated files that are not part of the deployable site."""
    for path in build_dir.rglob("*"):
        if path.is_file() and path.name not in _KEEP_NAMES and path.suffix not in _KEEP_SUFFIXES:
            path.unlink()


def _copy_static(build_dir: Path) -> None:
    """copy the static assets into the build directory."""
    for item in Path("site/static").iterdir():
        dest = build_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)


def main() -> None:
    build_dir = Path(os.environ["BUILD_DIR"])
    build_dir.mkdir(parents=True, exist_ok=True)
    pages.main()
    facade.main()
    _clean(build_dir)
    _copy_static(build_dir)
    sitemap.main()
    minify.main()


if __name__ == "__main__":
    main()
