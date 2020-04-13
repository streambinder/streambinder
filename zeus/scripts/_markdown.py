#!/usr/bin/env python3

import markdown
import re


def _idfy(value):
    value = value.replace(' ', '-')
    return ''.join(c for c in value if c.isalnum() or c == '-').lower()


def _section_icon(id):
    if id == 'about':
        return 'fas fa-question'
    elif id == 'installation':
        return 'fas fa-cloud-download-alt'
    else:
        return 'fab fa-slack-hash'


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
            section_id = _idfy(section_name)
            html = html.replace(
                match.group(),
                '<h2 id="{}">{}</h2>'.format(section_id, section_name)
            )
            html_sections.append({
                'id': section_id,
                'name': section_name,
                'icon': _section_icon(section_id)
            })

    return html, html_sections


def extract(path):
    with open(path, 'r') as markdown_fd:
        return _parse_html(
            markdown.markdown(
                markdown_fd.read(),
                extensions=[
                    'fenced_code',
                    'codehilite'
                ],
            )
        )
