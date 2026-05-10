#!/usr/bin/env python3

from __future__ import annotations

from typing import Any

import yaml

_cache: dict[str, "Config"] = {}


class Config:
    def __init__(self, path: str) -> None:
        self.path = path
        self.data = Config.parse_yaml(path)

    def get(self, *keys: str) -> Any:
        value = self.data
        for key in keys:
            value = value[key]
        return value

    def raw(self) -> Any:
        return self.data

    @staticmethod
    def new(path: str) -> Config:
        if path in _cache:
            return _cache[path]

        _cache[path] = Config(path)
        return _cache[path]

    @staticmethod
    def dump_yaml(path: str, config: Any) -> None:
        with open(path, "w", encoding="utf-8") as yaml_fd:
            yaml.dump(config, yaml_fd)

    @staticmethod
    def parse_yaml(path: str) -> Any:
        with open(path, "r", encoding="utf-8") as yaml_fd:
            try:
                return yaml.safe_load(yaml_fd)
            except yaml.YAMLError as e:
                print(e)
                return None
