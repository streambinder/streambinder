#!/usr/bin/env python3

from __future__ import annotations

from config import Config as config


def title(primary_key: str, website_title: str) -> str:
    if primary_key != website_title:
        return f"{primary_key} — {website_title}"
    return website_title


def idfy(value: str) -> str:
    value = value.replace(" ", "-")
    return "".join(c for c in value if c.isalnum() or c == "-").lower()


def icon(identifier: str) -> str:
    icons = config.new("src/website.yml").get("icons")
    if f"section-{identifier}" in icons:
        return str(icons[f"section-{identifier}"])
    return str(icons["section-generic"])
