#!/usr/bin/env python3

import yaml

_cache: dict[str, str] = {}


class Config:
    def __init__(self, path):
        self.path = path
        self.data = Config.parse_yaml(path)

    def get(self, *keys):
        value = self.data
        for key in keys:
            value = value[key]
        return value

    def raw(self):
        return self.data

    @staticmethod
    def new(path):
        if path in _cache:
            return _cache[path]

        _cache[path] = Config(path)
        return _cache[path]

    @staticmethod
    def dump_yaml(path, config):
        with open(path, "w", encoding="utf-8") as yaml_fd:
            yaml.dump(config, yaml_fd)

    @staticmethod
    def parse_yaml(path):
        with open(path, "r", encoding="utf-8") as yaml_fd:
            try:
                return yaml.safe_load(yaml_fd)
            except yaml.YAMLError as e:
                print(e)
                return None
