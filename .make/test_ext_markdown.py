from __future__ import annotations

from pathlib import Path

from ext_markdown import _parse_html, _shift_headings, collapse_heading_gaps, extract


def test_shift_headings_moves_each_level_down() -> None:
    assert _shift_headings("<h1>Title</h1>") == "<h2>Title</h2>"
    assert _shift_headings("<h5>Deep</h5>") == "<h6>Deep</h6>"


def test_shift_headings_keeps_attributes_and_h6() -> None:
    assert _shift_headings('<h2 class="x">A</h2>') == '<h3 class="x">A</h3>'
    assert _shift_headings("<h6>Floor</h6>") == "<h6>Floor</h6>"


def test_collapse_heading_gaps_without_headings() -> None:
    assert collapse_heading_gaps("<p>plain</p>") == "<p>plain</p>"


def test_collapse_heading_gaps_already_compact() -> None:
    html = "<h2>A</h2><h3>B</h3>"
    assert collapse_heading_gaps(html) == html


def test_collapse_heading_gaps_remaps_levels() -> None:
    html = "<h2>A</h2><h4>B</h4><h5>C</h5>"
    assert collapse_heading_gaps(html) == "<h2>A</h2><h3>B</h3><h4>C</h4>"
    assert collapse_heading_gaps("<h4>Only</h4>") == "<h2>Only</h2>"


def test_parse_html_adds_section_ids() -> None:
    html, sections = _parse_html("<h1>About Me</h1>\n<p>body</p>\n<h1>Second Part</h1>\n")

    assert '<h2 id="about-me">About Me</h2>' in html
    assert '<h2 id="second-part">Second Part</h2>' in html
    assert sections == [
        {"id": "about-me", "name": "About Me"},
        {"id": "second-part", "name": "Second Part"},
    ]


def test_parse_html_rewrites_markdown_links_to_anchors() -> None:
    html, sections = _parse_html('<p><a href="design-notes.md">notes</a></p>')

    assert html == '<p><a href="#design-notes">notes</a></p>'
    assert sections == []


def test_parse_html_fills_alt_from_image_filename() -> None:
    html, _ = _parse_html('<img src="pics/my-cat_photo.jpg" alt="">')

    assert html == '<img src="pics/my-cat_photo.jpg" alt="my cat photo">'


def test_parse_html_fills_alt_without_source() -> None:
    html, _ = _parse_html('<img alt="">')

    assert html == '<img alt="image">'


def test_extract_renders_markdown_file(tmp_path: Path) -> None:
    path = tmp_path / "page.md"
    path.write_text("# Hello World\n\nSome **bold** text.\n", encoding="utf-8")

    html, sections = extract(str(path))

    assert '<h2 id="hello-world">Hello World</h2>' in html
    assert "<strong>bold</strong>" in html
    assert sections == [{"id": "hello-world", "name": "Hello World"}]
