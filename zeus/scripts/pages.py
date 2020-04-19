#!/usr/bin/env python3

import glob
import jinja2
import os
import subprocess
import sys
import yaml

from jinja2 import Template
from distutils.dir_util import copy_tree

from _config import Config as config
from _globals import get as zeus_global
from _html import title
from _markdown import extract as markdown
from _parser import get as parse

config_website = config.new('src/website.yaml')
if config_website is None:
    sys.exit('Unable to parse configuration file')

for page in config_website.get('pages'):

    # config
    page_config = {**config_website.raw(), **{'page': page}}

    # paths
    path = os.path.join(zeus_global('build_dir'), *page['path'].split("/"))
    path_html = os.path.join(path, '_index.html')
    path_yaml = os.path.join(path, '_index.yaml')
    path_content = os.path.join('src', page['content'])
    os.makedirs(path, exist_ok=True)

    # wiki page
    if os.path.isdir(path_content) and page['type'] == 'wiki':
        page_assets = os.path.join(path_content, 'assets')
        if os.path.isdir(page_assets):
            os.system('cp -rf {} {}'.format(page_assets, path))

        html_content = ''
        html_sections = []
        wiki_index = os.path.join(path_content, 'Home.md')
        wiki_index_entries, _ = subprocess.Popen(
            ['egrep', '-e', '\\([a-zA-Z]+\\)$', wiki_index],
            stdout=subprocess.PIPE).communicate()
        for wiki_page in [page.split('(')[1][:-1] + '.md' for page in wiki_index_entries.decode('utf-8').splitlines()]:
            html_sub_content, html_sub_sections = markdown(
                os.path.join(path_content, wiki_page))
            html_content += html_sub_content
            html_sections += html_sub_sections

        page_config = {
            **page_config,
            'page': {
                **page_config['page'],
                'content': html_content,
                'sections': html_sections
            }
        }
        path_content = os.path.join('src', page['parent'])

    # parse and dump
    parse(template=path_content,
          output=path_html,
          config=page_config)
    config.dump_yaml(path_yaml, {
        'html': {
            'head': {
                'title': title(page['name'], config_website.get('info', 'name'))
            }
        }
    })
