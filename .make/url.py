#!/usr/bin/env python3

import requests


def manipulate(url):
    if 'github.com' in url and 'releases/latest' in url:
        url = requests.get(url.split(
            'releases/latest')[0] + 'releases/latest').url.replace('/tag/', '/download/') + '/' + url.split('/')[-1]
    return url
