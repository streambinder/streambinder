#!/usr/bin/env python3

import glob
import jinja2
import os
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

    # markdown page
    if path_content.endswith('.md'):
        html_content, html_sections = markdown(path_content)
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
