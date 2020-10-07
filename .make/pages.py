#!/usr/bin/env python3

import glob
import jinja2
import os
import requests
import subprocess
import sys
import yaml

from jinja2 import Template
from distutils.dir_util import copy_tree

from config import Config as config
from ext_html import title
from ext_markdown import extract as markdown
from parser import get as parse
from url import manipulate as url_manipulate

config_website = config.new('src/website.yaml')
if config_website is None:
    sys.exit('Unable to parse configuration file')

for page in config_website.get('pages'):
    if 'type' not in page:
        page['type'] = 'generic'

    # config
    page_config = {**config_website.raw(), **{'page': page}}

    # paths
    path = os.path.join(os.environ['BUILD_DIR'], *page['path'].split("/"))
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
    # prebult page
    elif page['type'] == 'prefetch':
        page_config = {
            **page_config,
            'prefetch': requests.get(
                url_manipulate(page['content']), allow_redirects=True).content.decode('utf-8')
        }
        for variant in range(len(page_config['page']['variants'])):
            page_config['page']['variants'][variant]['url'] = url_manipulate(
                page_config['page']['variants'][variant]['url'])
        path_content = os.path.join('src', page['parent'])

    # parse and dump
    parse(template=path_content,
          output=path_html,
          config=page_config)
    config.dump_yaml(path_yaml, {
        'html': {
            'head': {
                'title': title(page['name'], config_website.get('info', 'name')),
                'metadata': {
                    'title': title(page['name'], config_website.get('info', 'name')),
                    'description': page['description'],
                    'image': page['image'] or 'index.png',
                    'url': ''.join([config_website.get('info', 'website'), page['path']]),
                }
            }
        },
        'page': page
    })
