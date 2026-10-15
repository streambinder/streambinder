#!/usr/bin/env python3

from __future__ import annotations

import os

from streambinder.config import Config as config
from streambinder.config import load_site
from streambinder.jinja_parser import get as parse


def main() -> None:
    site_info = load_site("site/website.yml").info.model_dump()
    for fdir, _, fnames in os.walk(os.environ["BUILD_DIR"]):
        for fname in fnames:
            if fname != "_index.html":
                continue

            fname_html = os.path.join(fdir, fname)

            with open(fname_html, "r", encoding="utf-8") as html_fd:
                cfg = config.new(fname_html.replace("html", "yaml"))
                cfg.data["html"]["body"] = html_fd.read()
                # hoist site-level info (social, etc.) into facade scope
                cfg.data["info"] = site_info
                parse(
                    template="site/facade.html.j2",
                    output=os.path.join(fdir, "index.html"),
                    config=cfg.data,
                )


if __name__ == "__main__":
    main()
