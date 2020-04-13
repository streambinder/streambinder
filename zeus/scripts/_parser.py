#!/usr/bin/env python3

import jinja2
import os
import yaml


def get(template, output, config):
    return jinja2.Environment(
        block_start_string='{!',
        block_end_string='!}',
        variable_start_string='{{',
        variable_end_string='}}',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath('.'))
    ).get_template(template).stream(config).dump(output)
