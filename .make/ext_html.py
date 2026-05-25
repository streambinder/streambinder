#!/usr/bin/env python3

from __future__ import annotations


def title(primary_key: str, website_title: str) -> str:
    if primary_key != website_title:
        return f"{primary_key} — {website_title}"
    return website_title


def idfy(value: str) -> str:
    value = value.replace(" ", "-")
    return "".join(c for c in value if c.isalnum() or c == "-").lower()
