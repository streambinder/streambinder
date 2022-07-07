#!/usr/bin/env python3

import os
import subprocess
import sys

from config import Config as config

font_mono = 'Overpass-Mono-Regular-Nerd-Font-Complete-Mono'
font_mono_bold = 'Overpass-Mono-Bold-Nerd-Font-Complete-Mono'
for fdir, _, fnames in os.walk(os.environ['BUILD_DIR']):
    for fname in fnames:
        if fname != '_index.yaml':
            continue

        cfg = config.new(os.path.join(fdir, fname))
        if cfg.get('html', 'head', 'metadata', 'image') not in ['', 'index.png'] or cfg.get('html', 'head', 'metadata', 'title') is None or cfg.get('html', 'head', 'metadata', 'description') is None:
            continue

        subprocess.Popen(
            ['convert', '-background', 'rgba(0,0,0,0)', '-fill', 'white', '-gravity', 'center', '-size', '3600x1881', '-pointsize',
             '300', '-kerning', '-150', '-font', font_mono_bold, 'caption:{}'.format(
                 cfg.get('page', 'name').upper()), '_index-title.png'], cwd=fdir).communicate()
        subprocess.Popen(
            ['convert', '-background', 'rgba(0,0,0,0)', '-fill', 'white', '-gravity', 'center', '-size', '3200x1881', '-pointsize',
             '150', '-kerning', '-75', '-font', font_mono, 'caption:{}'.format(
                 cfg.get('page', 'description')), '_index-desc.png'], cwd=fdir).communicate()
        subprocess.Popen(
            ['convert', '-define', 'png:bit-depth=8', '-size', '3600x1881', 'xc:transparent', '_index-title.png',
             '-geometry', '+50-250', '-composite', '_index-desc.png', '-geometry', '+200+300', '-composite', cfg.get('html', 'head', 'metadata', 'image')], cwd=fdir).communicate()
        subprocess.Popen(
            ['convert', '-background', '#383838', '-alpha', 'remove', '-alpha', 'off', '-shave', '50', '-border', '25', '-bordercolor', 'white',
             cfg.get('html', 'head', 'metadata', 'image'), cfg.get('html', 'head', 'metadata', 'image')], cwd=fdir).communicate()
        subprocess.Popen(
            ['convert', '-border', '25', '-bordercolor', '#383838', cfg.get('html', 'head', 'metadata', 'image'), cfg.get('html', 'head', 'metadata', 'image')], cwd=fdir).communicate()

        for tmp in ['_index-title.png', '_index-desc.png']:
            os.rename(os.path.join(fdir, tmp), os.path.join(
                fdir, tmp.replace('png', 'tmp')))
