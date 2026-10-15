#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

_EXTENSIONS = {"css", "js", "json", "svg", "xml"}


def minify_file(path: Path) -> None:
    args = ["minify"]
    if path.suffix == ".html":
        args.append("--html-keep-quotes")
    elif path.suffix[1:] not in _EXTENSIONS:
        return

    fd, tmp_name = tempfile.mkstemp()
    os.close(fd)
    try:
        subprocess.run([*args, str(path), "-o", tmp_name], check=True)
        shutil.move(tmp_name, path)
    except BaseException:
        Path(tmp_name).unlink(missing_ok=True)
        raise


def main() -> None:
    build_dir = Path(os.environ["BUILD_DIR"])
    for path in sorted(build_dir.rglob("*")):
        if path.is_file():
            minify_file(path)


if __name__ == "__main__":
    main()
