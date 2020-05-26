#!/usr/bin/env python3

import glob
import jinja2
import os
import sys
import yaml

from jinja2 import Template
from distutils.dir_util import copy_tree

from config import Config as config
from parser import get as parse


for fdir, _, fnames in os.walk(os.environ['BUILD_DIR']):
    for fname in fnames:
        if fname != '_index.html':
            continue

        fname_html = os.path.join(fdir, fname)

        with open(fname_html, 'r') as html_fd:
            parse(template='src/facade.html',
                  output=os.path.join(fdir, 'index.html'),
                  config={
                      'html': {
                          **config.new(fname_html.replace('html', 'yaml')).get('html'),
                          **{'body': html_fd.read()}
                      }
                  })
