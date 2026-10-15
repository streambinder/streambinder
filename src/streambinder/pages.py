#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from typing import Any
from urllib.parse import urlparse
from urllib.request import urlopen

from streambinder.config import Config as config
from streambinder.ext_html import title
from streambinder.ext_markdown import collapse_heading_gaps
from streambinder.ext_markdown import extract as markdown
from streambinder.jinja_parser import get as parse


def _build_jsonld(page: dict[str, Any], info: dict[str, Any], url: str) -> str:
    """build a JSON-LD object from the page's jsonld config and site info."""
    jsonld_cfg = page.get("jsonld")
    if not jsonld_cfg:
        return ""

    person = {"@type": "Person", "name": info["name"], "jobTitle": info["role"]}
    schema_type = jsonld_cfg["type"]

    if schema_type == "ProfilePage":
        # sameAs only includes absolute urls (skip relative paths like /resume)
        person["url"] = url
        person["sameAs"] = [s["url"] for s in info.get("social", []) if s["url"].startswith("http")]
        obj: dict[str, Any] = {"@type": "ProfilePage", "mainEntity": person}
    elif schema_type == "Person":
        person["url"] = url
        obj = person
    elif schema_type == "SoftwareSourceCode":
        obj = {
            "@type": "SoftwareSourceCode",
            "name": page["name"],
            "description": page["description"],
            "url": url,
            "codeRepository": page["url"],
            "author": person,
        }
    else:
        return ""

    return json.dumps({"@context": "https://schema.org", **obj}, indent=4)


def _doc_entries(index_file: str) -> list[str]:
    """list the markdown files a doc index links to, in order of appearance."""
    with open(index_file, encoding="utf-8") as fd:
        return re.findall(r"[a-z_\-]+\.md", fd.read())


def _wiki_entries(index_file: str) -> list[str]:
    """list the link lines of a wiki index, in order of appearance."""
    with open(index_file, encoding="utf-8") as fd:
        return [line for line in fd.read().splitlines() if re.search(r"\([a-zA-Z]+\)$", line)]


def _entry_pages(entries: list[str]) -> list[str]:
    """map index entries to markdown filenames: doc entries are plain
    filenames, wiki ones look like "- [Page](Name)"."""
    return [entry.split("(")[1][:-1] + ".md" if "(" in entry else entry for entry in entries]


def _aggregate_markdown(
    path_content: str, entries: list[str], dest: str
) -> tuple[str, list[dict[str, str]]]:
    """render the markdown pages of an index into concatenated html."""
    page_assets = os.path.join(path_content, "assets")
    if os.path.isdir(page_assets):
        shutil.copytree(page_assets, os.path.join(dest, "assets"), dirs_exist_ok=True)

    html_content = ""
    html_sections: list[dict[str, str]] = []
    for doc_page in _entry_pages(entries):
        sub_content, sub_sections = markdown(os.path.join(path_content, doc_page))
        html_content += sub_content
        html_sections += sub_sections
    return collapse_heading_gaps(html_content), html_sections


def _dump_markdown_sibling(path_content: str, entries: list[str], dest: str) -> None:
    """write the raw markdown sources of a page concatenated into a sibling index.md."""
    md_concat = ""
    for md_page in _entry_pages(entries):
        with open(os.path.join(path_content, md_page), encoding="utf-8") as md_fd:
            md_concat += md_fd.read().rstrip() + "\n\n"
    with open(os.path.join(dest, "index.md"), "w", encoding="utf-8") as md_fd:
        md_fd.write(md_concat.rstrip() + "\n")


def main() -> None:
    config_website = config.new("site/website.yml")
    if config_website is None:
        sys.exit("Unable to parse configuration file")

    for page in config_website.get("pages"):
        if "type" not in page:
            page["type"] = "generic"

        # link pages point at an external site: no local page to build
        if page["type"] == "link":
            continue

        # config
        page_config: dict[str, Any] = {**config_website.raw(), "page": page}

        # paths
        path = os.path.join(os.environ["BUILD_DIR"], *page["path"].split("/"))
        path_html = os.path.join(path, "_index.html")
        path_yaml = os.path.join(path, "_index.yaml")
        path_content = os.path.join("site", page["content"])
        os.makedirs(path, exist_ok=True)

        if os.path.isdir(path_content) and page["type"] == "doc":
            entries = _doc_entries(os.path.join(path_content, "README.md"))
            html_content, html_sections = _aggregate_markdown(path_content, entries, path)
            _dump_markdown_sibling(path_content, entries, path)
            page_config = {
                **page_config,
                "page": {
                    **page_config["page"],
                    "content": html_content,
                    "sections": html_sections,
                },
            }
            path_content = os.path.join("site", page["parent"])
        # wiki page
        elif os.path.isdir(path_content) and page["type"] == "wiki":
            entries = _wiki_entries(os.path.join(path_content, "Home.md"))
            html_content, html_sections = _aggregate_markdown(path_content, entries, path)
            _dump_markdown_sibling(path_content, entries, path)
            page_config = {
                **page_config,
                "page": {
                    **page_config["page"],
                    "content": html_content,
                    "sections": html_sections,
                },
            }
            path_content = os.path.join("site", page["parent"])
        # prebuilt page
        elif page["type"] == "prefetch":
            prefetch_url = page["content"]
            # pin to a specific erro release when the tag is propagated through the dispatch payload,
            # otherwise fall back to /latest/ which can serve stale content for ~5min after a release
            erro_tag = os.environ.get("ERRO_RELEASE_TAG", "").strip()
            if erro_tag:
                prefetch_url = prefetch_url.replace(
                    "/releases/latest/download/", f"/releases/download/{erro_tag}/"
                )
            # strip h1 from prefetched content — the page template provides its own
            with urlopen(prefetch_url, timeout=30) as response:
                prefetch_html = response.read().decode("utf-8")
            prefetch_html = re.sub(r"<h1[^>]*>.*?</h1>", "", prefetch_html, flags=re.DOTALL)
            page_config = {
                **page_config,
                "prefetch": prefetch_html,
            }
            path_content = os.path.join("site", page["parent"])

        # parse and dump
        parse(template=path_content, output=path_html, config=page_config)
        page_url = config_website.get("info", "website") + page["path"]
        config.dump_yaml(
            path_yaml,
            {
                "html": {
                    "head": {
                        "title": title(page["name"], config_website.get("info", "name")),
                        "metadata": {
                            "title": title(page["name"], config_website.get("info", "name")),
                            "description": page["description"],
                            "url": page_url,
                            "domain": urlparse(config_website.get("info", "website")).netloc,
                        },
                        "jsonld": _build_jsonld(page, config_website.get("info"), page_url),
                    }
                },
                "page": page,
            },
        )


if __name__ == "__main__":
    main()
