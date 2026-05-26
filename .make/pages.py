#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
from typing import Any
from urllib.parse import urlparse

import requests
from config import Config as config
from ext_html import title
from ext_markdown import extract as markdown
from jinja_parser import get as parse


def main() -> None:
    config_website = config.new("src/website.yml")
    if config_website is None:
        sys.exit("Unable to parse configuration file")

    for page in config_website.get("pages"):
        if "type" not in page:
            page["type"] = "generic"

        # config
        page_config: dict[str, Any] = {**config_website.raw(), **{"page": page}}

        # paths
        path = os.path.join(os.environ["BUILD_DIR"], *page["path"].split("/"))
        path_html = os.path.join(path, "_index.html")
        path_yaml = os.path.join(path, "_index.yaml")
        path_content = os.path.join("src", page["content"])
        os.makedirs(path, exist_ok=True)

        if os.path.isdir(path_content) and page["type"] == "doc":
            page_assets = os.path.join(path_content, "assets")
            if os.path.isdir(page_assets):
                os.system(f"cp -rf {page_assets} {path}")

            html_content = ""
            html_sections: list[dict[str, str]] = []
            doc_index = os.path.join(path_content, "README.md")
            with subprocess.Popen(["grep", "-oE", r"[a-z_\-]+\.md", doc_index], stdout=subprocess.PIPE) as proc:
                doc_index_entries, _ = proc.communicate()
            for doc_page in doc_index_entries.decode("utf-8").splitlines():
                html_sub_content, html_sub_sections = markdown(os.path.join(path_content, doc_page))
                html_content += html_sub_content
                html_sections += html_sub_sections
            page_config = {
                **page_config,
                "page": {
                    **page_config["page"],
                    "content": html_content,
                    "sections": html_sections,
                },
            }
            path_content = os.path.join("src", page["parent"])
        # wiki page
        elif os.path.isdir(path_content) and page["type"] == "wiki":
            page_assets = os.path.join(path_content, "assets")
            if os.path.isdir(page_assets):
                os.system(f"cp -rf {page_assets} {path}")

            html_content = ""
            html_sections = []
            wiki_index = os.path.join(path_content, "Home.md")
            with subprocess.Popen(["egrep", "-e", "\\([a-zA-Z]+\\)$", wiki_index], stdout=subprocess.PIPE) as proc:
                wiki_index_entries, _ = proc.communicate()
            for wiki_page in [wp.split("(")[1][:-1] + ".md" for wp in wiki_index_entries.decode("utf-8").splitlines()]:
                html_sub_content, html_sub_sections = markdown(os.path.join(path_content, wiki_page))
                html_content += html_sub_content
                html_sections += html_sub_sections

            page_config = {
                **page_config,
                "page": {
                    **page_config["page"],
                    "content": html_content,
                    "sections": html_sections,
                },
            }
            path_content = os.path.join("src", page["parent"])
        # prebuilt page
        elif page["type"] == "prefetch":
            prefetch_url = page["content"]
            # pin to a specific erro release when the tag is propagated through the dispatch payload,
            # otherwise fall back to /latest/ which can serve stale content for ~5min after a release
            erro_tag = os.environ.get("ERRO_RELEASE_TAG", "").strip()
            if erro_tag:
                prefetch_url = prefetch_url.replace("/releases/latest/download/", f"/releases/download/{erro_tag}/")
            page_config = {
                **page_config,
                "prefetch": requests.get(prefetch_url, timeout=30).content.decode("utf-8"),
            }
            path_content = os.path.join("src", page["parent"])

        # parse and dump
        parse(template=path_content, output=path_html, config=page_config)
        config.dump_yaml(
            path_yaml,
            {
                "html": {
                    "head": {
                        "title": title(page["name"], config_website.get("info", "name")),
                        "metadata": {
                            "title": title(page["name"], config_website.get("info", "name")),
                            "description": page["description"],
                            "url": "/".join([config_website.get("info", "website"), page["path"]]),
                            "domain": urlparse(config_website.get("info", "website")).netloc,
                        },
                    }
                },
                "page": page,
            },
        )


if __name__ == "__main__":
    main()
