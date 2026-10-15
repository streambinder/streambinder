from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from streambinder.config import Config, load_site


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_parse_yaml_returns_mapping(tmp_path: Path) -> None:
    path = tmp_path / "site.yml"
    _write(path, "info:\n  name: Davide\n  role: Engineer\n")

    assert Config.parse_yaml(str(path)) == {"info": {"name": "Davide", "role": "Engineer"}}


def test_parse_yaml_invalid_returns_none(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "broken.yml"
    _write(path, "info: [unclosed\n")

    assert Config.parse_yaml(str(path)) is None
    assert capsys.readouterr().out != ""


def test_parse_yaml_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        Config.parse_yaml(str(tmp_path / "missing.yml"))


def test_get_walks_nested_keys(tmp_path: Path) -> None:
    path = tmp_path / "site.yml"
    _write(path, "info:\n  name: Davide\npages:\n  - path: /\n")

    cfg = Config(str(path))

    assert cfg.path == str(path)
    assert cfg.get("info", "name") == "Davide"
    assert cfg.get("pages") == [{"path": "/"}]
    assert cfg.raw() == {"info": {"name": "Davide"}, "pages": [{"path": "/"}]}


def test_dump_yaml_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "out.yml"
    data = {"html": {"head": {"title": "Home"}}, "page": {"name": "Home"}}

    Config.dump_yaml(str(path), data)

    assert Config.parse_yaml(str(path)) == data


_SITE_YML = """\
info:
  name: Davide
  role: Engineer
  website: https://example.com
  social:
    - name: GitHub
      url: https://example.com/gh
pages:
  - path: /
    name: Home
  - path: /doc/x
    type: doc
    jsonld:
      type: SoftwareSourceCode
"""


def test_load_site_validates_and_defaults(tmp_path: Path) -> None:
    path = tmp_path / "website.yml"
    _write(path, _SITE_YML)

    site = load_site(str(path))

    assert site.info.name == "Davide"
    assert site.info.social[0].url == "https://example.com/gh"
    assert site.pages[0].type == "generic"
    assert site.pages[1].jsonld is not None
    assert site.pages[1].jsonld.type == "SoftwareSourceCode"


def test_load_site_rejects_missing_info(tmp_path: Path) -> None:
    path = tmp_path / "website.yml"
    _write(path, "pages: []\n")

    with pytest.raises(ValidationError):
        load_site(str(path))


def test_load_site_rejects_page_without_path(tmp_path: Path) -> None:
    path = tmp_path / "website.yml"
    _write(path, _SITE_YML + "  - name: NoPath\n")

    with pytest.raises(ValidationError):
        load_site(str(path))


def test_new_caches_by_path(tmp_path: Path) -> None:
    first = tmp_path / "first.yml"
    second = tmp_path / "second.yml"
    _write(first, "value: 1\n")
    _write(second, "value: 2\n")

    assert Config.new(str(first)) is Config.new(str(first))
    assert Config.new(str(first)) is not Config.new(str(second))
    assert Config.new(str(second)).get("value") == 2
