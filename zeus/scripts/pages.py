#!/usr/bin/env python3

import glob
import jinja2
import os
import sys
import yaml

from jinja2 import Template
from distutils.dir_util import copy_tree


parser = jinja2.Environment(
    block_start_string='{!',
    block_end_string='!}',
    variable_start_string='{{',
    variable_end_string='}}',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.abspath('.'))
)

config = None
with open('src/website.yaml', 'r') as config_fd:
    try:
        config = yaml.safe_load(config_fd)
    except yaml.YAMLError as e:
        print(e)
if config is None:
    print('unable to parse {}'.format(config))
    sys.exit(1)


for page in config['pages']:
    path_local = os.path.join('public', *page['path'].split('/'))
    path_local_html = os.path.join(path_local, '_index.html')
    path_local_yaml = os.path.join(path_local, '_index.yaml')
    path_content = os.path.join('src', *page['content'].split('/'))
    page_config = {**config, **{'page': page}}
    os.makedirs(path_local, exist_ok=True)
    parser.get_template(path_content).stream(
        page_config).dump(path_local_html)
    with open(path_local_yaml, 'w') as yaml_fd:
        yaml.dump({'title': page['title'] if page['title'] == config['info']['name']
                   else '{} | {}'.format(page['title'], config['info']['name'])}, yaml_fd)

for project in config['projects']:
    path_local = os.path.join('public', 'doc', project['name'].lower())
    path_local_html = os.path.join(path_local, '_index.html')
    path_local_yaml = os.path.join(path_local, '_index.yaml')
    path_proj_yaml = os.path.join(path_local, '_proj.yaml')
    proj_config = None
    with open(path_proj_yaml, 'r') as proj_config_fd:
        try:
            proj_config = yaml.safe_load(proj_config_fd)
        except yaml.YAMLError as e:
            print(e)
            sys.exit(1)

    # process markdown: path_content = os.path.join('src', *project['content'].split('/'))
    path_content = os.path.join('src', 'pages', 'project.html')
    project_config = {**config, **{'project': {**project, **proj_config}}}
    os.makedirs(path_local, exist_ok=True)
    parser.get_template(path_content).stream(
        project_config).dump(path_local_html)
    with open(path_local_yaml, 'w') as yaml_fd:
        yaml.dump({'title': page['title'] if page['title'] == config['info']['name']
                   else '{} | {}'.format(page['title'], config['info']['name'])}, yaml_fd)
