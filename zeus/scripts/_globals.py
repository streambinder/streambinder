#!/usr/bin/env python3

import os


def get(key):
    return os.environ['zeus.{}'.format(key)]
