"""
Tests for the HTML renderer pipeline (adamsquotes.pipeline.html_renderer).
"""

from __future__ import annotations

from pathlib import Path

from adamsquotes.pipeline.html_renderer import (
    parse_quotes,
    render_toc,
    render_quote_html,
    generate_html,
    write_html,
    _add_column_classes,
)
from tests.conftest import SAMPLE_MD, SAMPLE_HEADER


class TestParseQuotes:
    def test_parses_multiple_quotes(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert len(quotes) == 3

    def test_parses_quote_text(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert "fortune favours the bold" in quotes[0].quote

    def test_parses_source(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert quotes[0].source == "reddit r/perth"

    def test_parses_author(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert quotes[0].author == "Captain-Peacock"

    def test_parses_link(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert "reddit.com" in quotes[0].link

    def test_parses_note(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert "sensory processing" in quotes[1].note

    def test_empty_note_becomes_empty_string(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert quotes[2].note == ""

    def test_generates_titles_for_all_quotes(self):
        quotes = parse_quotes(SAMPLE_MD)
        assert all(q.title != "" for q in quotes)


class TestRenderQuoteHtml:
    def test_basic_div_structure(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = render_quote_html(quotes[0])
        assert '<div class="quote"' in html
        assert f'id="{quotes[0].id_for_quote}"' in html
        assert "</div>" in html

    def test_contains_title(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = render_quote_html(quotes[0])
        assert '<p class="quote-title">' in html

    def test_contains_source_tagged(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = render_quote_html(quotes[0])
        assert '<span class="source-source">Source:</span>' in html

    def test_contains_author_tagged(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = render_quote_html(quotes[0])
        assert '<span class="tag-author">Author:</span>' in html

    def test_contains_link_tagged(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = render_quote_html(quotes[0])
        assert '<span class="tag-link">Link:</span>' in html

    def test_contains_note_tagged(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = render_quote_html(quotes[1])
        assert '<p class="note">' in html


class TestRenderToc:
    def test_has_div_wrapper(self):
        quotes = parse_quotes(SAMPLE_MD)
        toc = render_toc(quotes)
        assert toc.startswith('<div class="table-of-contents">')
        assert toc.strip().endswith("</div>")

    def test_contains_links(self):
        quotes = parse_quotes(SAMPLE_MD)
        toc = render_toc(quotes)
        for q in quotes:
            assert f'href="#{q.id_for_quote}"' in toc


class TestGenerateHtml:
    def test_injects_table_of_contents(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = generate_html(quotes, SAMPLE_HEADER)
        assert '<div class="table-of-contents">' in html
        assert '<a class="tableOfContents"' in html

    def test_injects_quotes(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = generate_html(quotes, SAMPLE_HEADER)
        assert '<div class="quote"' in html
        assert "fortune favours the bold" in html

    def test_replaces_all_placeholders(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = generate_html(quotes, SAMPLE_HEADER)
        assert "<!-- table of contents -->" not in html
        assert "<!--quotes-->" not in html

    def test_contains_doctype(self):
        quotes = parse_quotes(SAMPLE_MD)
        html = generate_html(quotes, SAMPLE_HEADER)
        assert html.startswith("<!DOCTYPE html>")


class TestWriteHtml:
    def test_writes_html_file(self, tmp_path):
        quotes = parse_quotes(SAMPLE_MD)

        header_file = tmp_path / "Header.html"
        header_file.write_text(SAMPLE_HEADER, encoding="utf-8")
        output_file = tmp_path / "output.html"

        write_html(quotes, output_path=output_file, header_path=header_file)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "fortune favours the bold" in content

    def test_default_output(self, tmp_path):
        quotes = parse_quotes(SAMPLE_MD)

        header_file = tmp_path / "Header.html"
        header_file.write_text(SAMPLE_HEADER, encoding="utf-8")

        cwd = Path.cwd()
        try:
            __import__("os").chdir(tmp_path)
            write_html(quotes)
        finally:
            __import__("os").chdir(str(cwd))

        assert (tmp_path / "index.html").exists()


class TestAddColumnClasses:
    def test_adds_classes_to_th(self):
        table = "<table><tr><th>title</th><th>source</th></tr></table>"
        result = _add_column_classes(table)
        assert 'class="column0"' in result

    def test_adds_classes_to_td(self):
        table = "<table>\n<tr>\n<td>Hello</td>\n<td>World</td>\n</tr>\n</table>"
        result = _add_column_classes(table)
        assert 'class="column0"' in result
        assert 'class="column1"' in result
