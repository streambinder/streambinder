#!/usr/bin/env python3

from __future__ import annotations

import re

import markdown
from ext_html import idfy


def _shift_headings(html: str) -> str:
    """shift all headings down one level (h1→h2 etc.)."""

    def _replace_tag(match: re.Match[str]) -> str:
        return f"<{'/' if match.group(1) else ''}h{int(match.group(2)) + 1}{match.group(3)}"

    return re.sub(r"<(/?)h([1-5])([\s>])", _replace_tag, html)


def collapse_heading_gaps(html: str) -> str:
    """collapse heading level gaps in the final concatenated html so the
    structure never skips a level (e.g. {2,4,5} → {2,3,4})."""
    used = sorted({int(m.group(1)) for m in re.finditer(r"<h([2-6])[\s>]", html)})
    if not used:
        return html
    remap = {level: i + 2 for i, level in enumerate(used)}
    if all(level == target for level, target in remap.items()):
        return html

    def _remap_tag(match: re.Match[str]) -> str:
        return f"<{'/' if match.group(1) else ''}h{remap[int(match.group(2))]}{match.group(3)}"

    return re.sub(r"<(/?)h([2-6])([\s>])", _remap_tag, html)


def _parse_html(html: str) -> tuple[str, list[dict[str, str]]]:
    html = _shift_headings(html)
    # rewrite relative .md links to same-page anchors (all md files render
    # as sections on a single page, so about.md → #about, design.md → #design)
    html = re.sub(
        r'href="([a-zA-Z0-9_\-]+)\.md"',
        lambda m: f'href="#{idfy(m.group(1))}"',
        html,
    )

    # fill empty alt attributes on images — derive alt from the filename
    def _fill_alt(match: re.Match[str]) -> str:
        src = re.search(r'src="([^"]+)"', match.group(0))
        if not src:
            return match.group(0).replace('alt=""', 'alt="image"')
        name = src.group(1).rsplit("/", 1)[-1].rsplit(".", 1)[0]
        alt = name.replace("-", " ").replace("_", " ")
        return match.group(0).replace('alt=""', f'alt="{alt}"')

    html = re.sub(r"<img[^>]* alt=\"\"[^>]*>", _fill_alt, html)
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
