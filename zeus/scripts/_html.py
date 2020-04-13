#!/usr/bin/env python3

import jinja2
import os
import yaml


def title(primary_key, website_title):
    return '{} | {}'.format(primary_key, website_title) if primary_key != website_title else website_title
