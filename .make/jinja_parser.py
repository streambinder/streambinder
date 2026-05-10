#!/usr/bin/env python3

from __future__ import annotations

import os
from typing import Any

import jinja2


def get(template: str, output: str, config: dict[str, Any]) -> None:
    jinja2.Environment(
        block_start_string="{!",
        block_end_string="!}",
        variable_start_string="{{",
        variable_end_string="}}",
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath(".")),
    ).get_template(template).stream(config).dump(output)
