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

for subdir, dirs, files in os.walk('public'):
    for fname in files:
        if fname != '_index.html':
            continue

        fname_html = os.path.join(subdir, fname)
        fname_yaml = fname_html.replace('html', 'yaml')
        config_html = None
        config_yaml = None
        with open(fname_html, 'r') as html_fd:
            config_html = html_fd.read()
        with open(fname_yaml, 'r') as yaml_fd:
            try:
                config_yaml = yaml.safe_load(yaml_fd)
            except yaml.YAMLError as e:
                print(e)
                sys.exit(1)
        if config_yaml is None:
            print('unable to parse {}'.format(fname_yaml))
            sys.exit(1)
        parser.get_template('src/facade.html').stream(
            {**config_yaml, 'content': config_html}).dump(os.path.join(subdir, 'index.html'))
