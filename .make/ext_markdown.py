#!/usr/bin/env python3

from __future__ import annotations

import re

import markdown
from ext_html import idfy


def _pre_parse_html(html: str) -> str:
    html = html.replace("h5>", "h6>")
    html = html.replace("h4>", "h5>")
    html = html.replace("h3>", "h4>")
    html = html.replace("h2>", "h3>")
    return html.replace("h1>", "h2>")


def _parse_html(html: str) -> tuple[str, list[dict[str, str]]]:
    html = _pre_parse_html(html)
    html_sections: list[dict[str, str]] = []

    matches = re.finditer(r"<h2>(.*)</h2>", html, re.MULTILINE)
    for _, match in enumerate(matches, start=1):
        for group in range(0, len(match.groups())):
            section_name = match.group(group + 1)
            section_id = idfy(section_name)
            html = html.replace(match.group(), f'<h2 id="{section_id}">{section_name}</h2>')
            html_sections.append({"id": section_id, "name": section_name})

    return html, html_sections


def extract(path: str) -> tuple[str, list[dict[str, str]]]:
    with open(path, "r", encoding="utf-8") as markdown_fd:
        return _parse_html(
            markdown.markdown(
                markdown_fd.read(),
                tab_length=2,
                extensions=[
                    "tables",
                    "fenced_code",
                    "codehilite",
                ],
            )
        )
