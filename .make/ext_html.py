#!/usr/bin/env python3

import jinja2
import os
import yaml

from config import Config as config


def title(primary_key, website_title):
    if primary_key != website_title:
        return '{} — {}'.format(primary_key, website_title)
    return website_title


def idfy(value):
    value = value.replace(' ', '-')
    return ''.join(c for c in value if c.isalnum() or c == '-').lower()


def icon(id):
    icons = config.new('src/website.yml').get('icons')
    if 'section-{}'.format(id) in icons:
        return icons['section-{}'.format(id)]
    return icons['section-generic']
