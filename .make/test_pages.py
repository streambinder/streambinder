from __future__ import annotations

import json
import runpy
from pathlib import Path
from typing import Any

import pages
import pytest
import requests
import yaml

_INFO: dict[str, Any] = {
    "name": "Test Person",
    "role": "Engineer",
    "social": [{"url": "https://example.com/gh"}, {"url": "/resume"}],
}


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _load_jsonld(page: dict[str, Any], info: dict[str, Any]) -> dict[str, Any]:
    raw = pages._build_jsonld(page, info, "https://example.com/page")
    parsed: dict[str, Any] = json.loads(raw)
    return parsed


def test_build_jsonld_without_config() -> None:
    assert pages._build_jsonld({}, _INFO, "https://example.com/") == ""


def test_build_jsonld_unknown_type() -> None:
    page = {"jsonld": {"type": "WebPage"}}
    assert pages._build_jsonld(page, _INFO, "https://example.com/") == ""


def test_build_jsonld_profile_page() -> None:
    parsed = _load_jsonld({"jsonld": {"type": "ProfilePage"}}, _INFO)

    assert parsed["@context"] == "https://schema.org"
    assert parsed["@type"] == "ProfilePage"
    person = parsed["mainEntity"]
    assert person["name"] == "Test Person"
    assert person["jobTitle"] == "Engineer"
    assert person["url"] == "https://example.com/page"
    assert person["sameAs"] == ["https://example.com/gh"]


def test_build_jsonld_profile_page_without_social() -> None:
    info = {"name": "Test Person", "role": "Engineer"}
    parsed = _load_jsonld({"jsonld": {"type": "ProfilePage"}}, info)

    assert parsed["mainEntity"]["sameAs"] == []


def test_build_jsonld_person() -> None:
    parsed = _load_jsonld({"jsonld": {"type": "Person"}}, _INFO)

    assert parsed["@type"] == "Person"
    assert parsed["name"] == "Test Person"
    assert parsed["url"] == "https://example.com/page"


def test_build_jsonld_software_source_code() -> None:
    page = {
        "jsonld": {"type": "SoftwareSourceCode"},
        "name": "Proj",
        "description": "A project",
        "url": "https://example.com/repo",
    }
    parsed = _load_jsonld(page, _INFO)

    assert parsed["@type"] == "SoftwareSourceCode"
    assert parsed["name"] == "Proj"
    assert parsed["codeRepository"] == "https://example.com/repo"
    assert parsed["author"]["name"] == "Test Person"


def test_aggregate_markdown_concatenates_pages(tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write(content / "index.txt", "alpha.md\nbeta.md\n")
    _write(content / "alpha.md", "# Alpha\n\nfirst\n")
    _write(content / "beta.md", "# Beta\n\nsecond\n")
    _write(content / "assets" / "asset.txt", "asset")
    dest = tmp_path / "build"
    dest.mkdir()

    html, sections = pages._aggregate_markdown(
        str(content), str(content / "index.txt"), ["cat"], str(dest)
    )

    assert '<h2 id="alpha">Alpha</h2>' in html
    assert '<h2 id="beta">Beta</h2>' in html
    assert sections == [
        {"id": "alpha", "name": "Alpha"},
        {"id": "beta", "name": "Beta"},
    ]
    assert (dest / "assets" / "asset.txt").read_text(encoding="utf-8") == "asset"


def test_aggregate_markdown_without_assets(tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write(content / "index.txt", "alpha.md\n")
    _write(content / "alpha.md", "# Alpha\n")

    html, sections = pages._aggregate_markdown(
        str(content), str(content / "index.txt"), ["cat"], str(tmp_path)
    )

    assert '<h2 id="alpha">Alpha</h2>' in html
    assert sections == [{"id": "alpha", "name": "Alpha"}]


def test_dump_markdown_sibling_plain_entries(tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write(content / "index.txt", "alpha.md\nbeta.md\n")
    _write(content / "alpha.md", "# Alpha\n")
    _write(content / "beta.md", "# Beta\n")
    dest = tmp_path / "build"
    dest.mkdir()

    pages._dump_markdown_sibling(str(content), str(content / "index.txt"), ["cat"], str(dest))

    assert (dest / "index.md").read_text(encoding="utf-8") == "# Alpha\n\n# Beta\n"


def test_dump_markdown_sibling_wiki_entries(tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write(content / "index.txt", "- [Guide](Guide)\n")
    _write(content / "Guide.md", "# Guide\n")
    dest = tmp_path / "build"
    dest.mkdir()

    pages._dump_markdown_sibling(str(content), str(content / "index.txt"), ["cat"], str(dest))

    assert (dest / "index.md").read_text(encoding="utf-8") == "# Guide\n"


def _prepare_site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, pages_yaml: str) -> Path:
    monkeypatch.chdir(tmp_path)
    website = "info:\n  name: Test Person\n  role: Engineer\n"
    website += "  website: https://example.com\npages:\n" + pages_yaml
    _write(tmp_path / "src" / "website.yml", website)
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    monkeypatch.setenv("BUILD_DIR", str(build_dir))
    monkeypatch.delenv("ERRO_RELEASE_TAG", raising=False)
    return build_dir


def _read_yaml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data


def test_main_generic_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir = _prepare_site(
        tmp_path,
        monkeypatch,
        "  - path: /about\n"
        "    content: pages/about.html.j2\n"
        "    name: About\n"
        "    description: about page\n",
    )
    _write(tmp_path / "src" / "pages" / "about.html.j2", "About {{ page.name }} of {{ info.name }}")

    pages.main()

    rendered = (build_dir / "about" / "_index.html").read_text(encoding="utf-8")
    assert rendered == "About About of Test Person"
    dumped = _read_yaml(build_dir / "about" / "_index.yaml")
    assert dumped["html"]["head"]["title"] == "About — Test Person"
    metadata = dumped["html"]["head"]["metadata"]
    assert metadata["description"] == "about page"
    assert metadata["url"] == "https://example.com/about"
    assert metadata["domain"] == "example.com"
    assert dumped["html"]["head"]["jsonld"] == ""
    assert dumped["page"]["type"] == "generic"


def test_main_doc_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir = _prepare_site(
        tmp_path,
        monkeypatch,
        "  - path: /doc/proj\n"
        "    name: Proj\n"
        "    type: doc\n"
        "    content: docs/proj/docs\n"
        "    parent: pages/project.html.j2\n"
        "    description: proj page\n"
        "    url: https://example.com/repo\n"
        "    jsonld:\n"
        "      type: SoftwareSourceCode\n",
    )
    docs = tmp_path / "src" / "docs" / "proj" / "docs"
    _write(docs / "README.md", "- [Intro](intro.md)\n- [Guide](guide.md)\n")
    _write(docs / "intro.md", "# Intro\n\nintro body\n")
    _write(docs / "guide.md", "# Guide\n\nguide body\n")
    _write(docs / "assets" / "asset.txt", "asset")
    _write(
        tmp_path / "src" / "pages" / "project.html.j2", "Doc {{ page.name }}: {{ page.content }}"
    )

    pages.main()

    rendered = (build_dir / "doc" / "proj" / "_index.html").read_text(encoding="utf-8")
    assert "Doc Proj:" in rendered
    assert '<h2 id="intro">Intro</h2>' in rendered
    assert '<h2 id="guide">Guide</h2>' in rendered
    sibling = (build_dir / "doc" / "proj" / "index.md").read_text(encoding="utf-8")
    assert sibling == "# Intro\n\nintro body\n\n# Guide\n\nguide body\n"
    assert (build_dir / "doc" / "proj" / "assets" / "asset.txt").exists()
    dumped = _read_yaml(build_dir / "doc" / "proj" / "_index.yaml")
    jsonld = json.loads(dumped["html"]["head"]["jsonld"])
    assert jsonld["@type"] == "SoftwareSourceCode"


def test_main_wiki_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir = _prepare_site(
        tmp_path,
        monkeypatch,
        "  - path: /doc/wiki\n"
        "    name: Wiki\n"
        "    type: wiki\n"
        "    content: wikis/wiki\n"
        "    parent: pages/project.html.j2\n"
        "    description: wiki page\n",
    )
    wiki = tmp_path / "src" / "wikis" / "wiki"
    _write(wiki / "Home.md", "- [Intro](Intro)\n- [Guide](Guide)\n")
    _write(wiki / "Intro.md", "# Wiki Intro\n\nintro body\n")
    _write(wiki / "Guide.md", "# Wiki Guide\n\nguide body\n")
    _write(wiki / "assets" / "asset.txt", "asset")
    _write(
        tmp_path / "src" / "pages" / "project.html.j2", "Wiki {{ page.name }}: {{ page.content }}"
    )

    pages.main()

    rendered = (build_dir / "doc" / "wiki" / "_index.html").read_text(encoding="utf-8")
    assert "Wiki Wiki:" in rendered
    assert '<h2 id="wiki-intro">Wiki Intro</h2>' in rendered
    assert '<h2 id="wiki-guide">Wiki Guide</h2>' in rendered
    sibling = (build_dir / "doc" / "wiki" / "index.md").read_text(encoding="utf-8")
    assert sibling == "# Wiki Intro\n\nintro body\n\n# Wiki Guide\n\nguide body\n"
    assert (build_dir / "doc" / "wiki" / "assets" / "asset.txt").exists()


class _FakeResponse:
    def __init__(self, content: bytes) -> None:
        self.content = content


def test_main_prefetch_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir = _prepare_site(
        tmp_path,
        monkeypatch,
        "  - path: /resume\n"
        "    name: Resume\n"
        "    type: prefetch\n"
        "    content: https://example.com/resume.html\n"
        "    parent: pages/resume.html.j2\n"
        "    description: resume page\n",
    )
    _write(tmp_path / "src" / "pages" / "resume.html.j2", "Resume: {{ prefetch }}")

    def fake_get(url: str, timeout: int = 0) -> _FakeResponse:
        return _FakeResponse(b"<h1>Hidden Title</h1><p>kept body</p>")

    monkeypatch.setattr(requests, "get", fake_get)

    pages.main()

    rendered = (build_dir / "resume" / "_index.html").read_text(encoding="utf-8")
    assert rendered == "Resume: <p>kept body</p>"


def test_main_prefetch_page_with_release_tag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    build_dir = _prepare_site(
        tmp_path,
        monkeypatch,
        "  - path: /resume\n"
        "    name: Resume\n"
        "    type: prefetch\n"
        "    content: https://example.com/releases/latest/download/web_en.html\n"
        "    parent: pages/resume.html.j2\n"
        "    description: resume page\n",
    )
    _write(tmp_path / "src" / "pages" / "resume.html.j2", "Resume: {{ prefetch }}")
    monkeypatch.setenv("ERRO_RELEASE_TAG", "v1.2.3")
    requested: list[str] = []

    def fake_get(url: str, timeout: int = 0) -> _FakeResponse:
        requested.append(url)
        return _FakeResponse(b"<p>body</p>")

    monkeypatch.setattr(requests, "get", fake_get)

    pages.main()

    assert requested == ["https://example.com/releases/download/v1.2.3/web_en.html"]
    rendered = (build_dir / "resume" / "_index.html").read_text(encoding="utf-8")
    assert rendered == "Resume: <p>body</p>"


def test_module_runs_as_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    build_dir = _prepare_site(
        tmp_path,
        monkeypatch,
        "  - path: /about\n"
        "    content: pages/about.html.j2\n"
        "    name: About\n"
        "    description: about page\n",
    )
    _write(tmp_path / "src" / "pages" / "about.html.j2", "About {{ page.name }}")

    runpy.run_module("pages", run_name="__main__")

    assert (build_dir / "about" / "_index.html").exists()
