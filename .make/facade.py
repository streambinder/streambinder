#!/usr/bin/env python3

import os

from config import Config as config
from jinja_parser import get as parse

for fdir, _, fnames in os.walk(os.environ["BUILD_DIR"]):
    for fname in fnames:
        if fname != "_index.html":
            continue

        fname_html = os.path.join(fdir, fname)

        with open(fname_html, "r", encoding="utf-8") as html_fd:
            cfg = config.new(fname_html.replace("html", "yaml"))
            cfg.data["html"]["body"] = html_fd.read()
            parse(
                template="src/facade.html.j2",
                output=os.path.join(fdir, "index.html"),
                config=cfg.data,
            )
