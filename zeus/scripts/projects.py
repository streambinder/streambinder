#!/usr/bin/env python3

import glob
import markdown
import os
import re
import sys
import yaml


def slugify(value):
    value = value.replace(' ', '-')
    return ''.join(c for c in value if c.isalnum() or c == '-').lower()


def get_content(html):
    regex = r'<h2>(.*)</h2>'
    matches = re.finditer(regex, html, re.MULTILINE)
    sections = []
    for _, match in enumerate(matches, start=1):
        for n_group in range(0, len(match.groups())):
            n_group += 1
            section_name = match.group(n_group)
            section_id = slugify(section_name)
            html = html.replace(
                match.group(), '<h2 id="{}">{}</h2>'.format(section_id, section_name))
            sections.append({'id': section_id, 'name': section_name})
    return {'content': html, 'sections': sections}


def post_parse(html):
    html = html.replace('h5>', 'h6>')
    html = html.replace('h4>', 'h5>')
    html = html.replace('h3>', 'h4>')
    html = html.replace('h2>', 'h3>')
    html = html.replace('h1>', 'h2>')
    return get_content(html)


for project in glob.glob('src/projects/*.md'):
    project_html = os.path.join('public', 'doc', os.path.basename(
        os.path.splitext(project)[0]))
    os.makedirs(project_html, exist_ok=True)
    with open(project, 'r') as project_fd:
        html = post_parse(
            markdown.markdown(project_fd.read()))
        with open(os.path.join(project_html, '_proj.yaml'), 'w') as yaml_fd:
            yaml.dump(html, yaml_fd)
