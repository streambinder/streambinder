#!/usr/bin/env python3

from __future__ import annotations

import os

from config import Config as config

# pages that should never appear in the sitemap
EXCLUDED_PATHS = {"/404", "/500"}


def main() -> None:
    site = config.new("src/website.yml")
    base_url = site.get("info", "website")

    urls = []
    for page in site.get("pages"):
        if page["path"] in EXCLUDED_PATHS:
            continue
        urls.append(base_url + page["path"])

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for url in urls:
        lines.append(f"  <url><loc>{url}</loc></url>")
    lines.append("</urlset>")

    dest = os.path.join(os.environ["BUILD_DIR"], "sitemap.xml")
    with open(dest, "w", encoding="utf-8") as fd:
        fd.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
