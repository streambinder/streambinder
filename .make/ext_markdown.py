#!/usr/bin/env python3

import markdown
import re


from ext_html import idfy, icon


def _pre_parse_html(html):
    html = html.replace('h5>', 'h6>')
    html = html.replace('h4>', 'h5>')
    html = html.replace('h3>', 'h4>')
    html = html.replace('h2>', 'h3>')
    return html.replace('h1>', 'h2>')


def _parse_html(html):
    html = _pre_parse_html(html)
    html_sections = []

    matches = re.finditer(r'<h2>(.*)</h2>', html, re.MULTILINE)
    for _, match in enumerate(matches, start=1):
        for group in range(0, len(match.groups())):
            section_name = match.group(group+1)
            section_id = idfy(section_name)
            html = html.replace(
                match.group(),
                '<h2 id="{}">{}</h2>'.format(section_id, section_name)
            )
            html_sections.append({
                'id': section_id,
                'name': section_name,
                'icon': icon(section_id)
            })

    return html, html_sections


def extract(path):
    with open(path, 'r') as markdown_fd:
        return _parse_html(
            markdown.markdown(
                markdown_fd.read(),
                tab_length=2,
                extensions=[
                    'tables',
                    'fenced_code',
                    'codehilite',
                ],
            )
        )
