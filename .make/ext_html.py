#!/usr/bin/env python3


from config import Config as config


def title(primary_key, website_title):
    if primary_key != website_title:
        return f"{primary_key} — {website_title}"
    return website_title


def idfy(value):
    value = value.replace(" ", "-")
    return "".join(c for c in value if c.isalnum() or c == "-").lower()


def icon(identifier):
    icons = config.new("src/website.yml").get("icons")
    if f"section-{identifier}" in icons:
        return icons[f"section-{identifier}"]
    return icons["section-generic"]
