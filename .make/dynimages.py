#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess

from config import Config as config

FONT_MONO = "Overpass-Mono-Light"
FONT_MONO_BOLD = "Overpass-Mono-Bold"


def main() -> None:
    for fdir, _, fnames in os.walk(os.environ["BUILD_DIR"]):
        for fname in fnames:
            if fname != "_index.yaml":
                continue

            cfg = config.new(os.path.join(fdir, fname))
            image_path = str(cfg.get("html", "head", "metadata", "image"))
            if "/" in image_path:
                image_path = image_path.rsplit("/", maxsplit=1)[-1]

            if (
                not (image_path == "" or image_path.endswith("index.png"))
                or cfg.get("html", "head", "metadata", "title") is None
                or cfg.get("html", "head", "metadata", "description") is None
            ):
                continue

            with subprocess.Popen(
                [
                    "magick",
                    "-background",
                    "rgba(0,0,0,0)",
                    "-fill",
                    "white",
                    "-gravity",
                    "center",
                    "-size",
                    "3600x1881",
                    "-pointsize",
                    "300",
                    "-font",
                    FONT_MONO_BOLD,
                    f"caption:{cfg.get('page', 'name').upper()}",
                    "_index-title.png",
                ],
                cwd=fdir,
            ):
                pass
            with subprocess.Popen(
                [
                    "magick",
                    "-background",
                    "rgba(0,0,0,0)",
                    "-fill",
                    "white",
                    "-gravity",
                    "center",
                    "-size",
                    "3200x1881",
                    "-pointsize",
                    "150",
                    "-font",
                    FONT_MONO,
                    f"caption:{cfg.get('page', 'description')}",
                    "_index-desc.png",
                ],
                cwd=fdir,
            ):
                pass
            with subprocess.Popen(
                [
                    "magick",
                    "-define",
                    "png:bit-depth=8",
                    "-size",
                    "3600x1881",
                    "xc:transparent",
                    "_index-title.png",
                    "-geometry",
                    "+50-250",
                    "-composite",
                    "_index-desc.png",
                    "-geometry",
                    "+200+300",
                    "-composite",
                    image_path,
                ],
                cwd=fdir,
            ):
                pass
            with subprocess.Popen(
                [
                    "magick",
                    "-background",
                    "#383838",
                    "-alpha",
                    "remove",
                    "-alpha",
                    "off",
                    "-shave",
                    "50",
                    "-border",
                    "25",
                    "-bordercolor",
                    "white",
                    image_path,
                    image_path,
                ],
                cwd=fdir,
            ):
                pass
            with subprocess.Popen(
                [
                    "magick",
                    "-border",
                    "25",
                    "-bordercolor",
                    "#383838",
                    image_path,
                    image_path,
                ],
                cwd=fdir,
            ):
                pass

            for tmp in ["_index-title.png", "_index-desc.png"]:
                os.rename(os.path.join(fdir, tmp), os.path.join(fdir, tmp.replace("png", "tmp")))


if __name__ == "__main__":
    main()
