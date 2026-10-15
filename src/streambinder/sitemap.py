#!/usr/bin/env python3

from __future__ import annotations

import os

from streambinder.config import load_site

# pages that should never appear in the sitemap
EXCLUDED_PATHS = {"/404", "/500"}


def main() -> None:
    site = load_site("site/website.yml")
    base_url = site.info.website

    urls = []
    for page in site.pages:
        if page.path in EXCLUDED_PATHS:
            continue
        if page.type == "link":
            continue
        urls.append(base_url + page.path)

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
