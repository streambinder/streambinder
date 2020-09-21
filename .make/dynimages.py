#!/usr/bin/env python3

import os
import subprocess
import sys

from config import Config as config

font_mono = None
for font in subprocess.Popen(
        ['convert', '-list', 'font'], stdout=subprocess.PIPE).communicate()[0].splitlines():
    font = font.strip().decode('utf8')
    if font.lower().endswith('mono'):
        font_mono = font.split()[-1]
        break
if not font_mono:
    print('Font not found')
    sys.exit(1)

for fdir, _, fnames in os.walk(os.environ['BUILD_DIR']):
    for fname in fnames:
        if fname != '_index.yaml':
            continue

        cfg = config.new(os.path.join(fdir, fname))
        if cfg.get('html', 'head', 'metadata', 'image') not in ['', 'index.png'] or cfg.get('html', 'head', 'metadata', 'title') is None or cfg.get('html', 'head', 'metadata', 'description') is None:
            continue

        subprocess.Popen(
            ['convert', '-fill', 'white', '-gravity', 'center', '-size', '3600x1881', 'xc:transparent', '-pointsize',
             '225', '-font', font_mono, '-draw', 'text 0,0 \'{}\''.format(
                 cfg.get('html', 'head', 'metadata', 'title')), '_index-title.png'], cwd=fdir).communicate()
        subprocess.Popen(
            ['convert', '-fill', 'white', '-gravity', 'center', '-size', '3600x1881', 'xc:transparent', '-pointsize',
             '125', '-font', font_mono, '-draw', 'text 0,0 \'{}\''.format(
                 cfg.get('html', 'head', 'metadata', 'description')), '_index-desc.png'], cwd=fdir).communicate()
        subprocess.Popen(
            ['convert', '-define', 'png:bit-depth=8', '-size', '3600x1881', 'xc:transparent', '_index-title.png',
             '-geometry', '+0-100', '-composite', '_index-desc.png', '-geometry', '+0+100', '-composite', '_index-alpha.png'], cwd=fdir).communicate()
        subprocess.Popen(
            ['convert', '-background', '#383838', '-alpha', 'remove', '-alpha', 'off',
             '_index-alpha.png', cfg.get('html', 'head', 'metadata', 'image')], cwd=fdir).communicate()

        for tmp in ['_index-title.png', '_index-desc.png', '_index-alpha.png']:
            os.rename(os.path.join(fdir, tmp), os.path.join(
                fdir, tmp.replace('png', 'tmp')))
