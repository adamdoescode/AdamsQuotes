"""
Tests for scripts/processQuotes.py — core logic and argparse interface,
all without touching real files (except tmp_path for main() integration).
"""

from pathlib import Path

import pytest

from scripts.processQuotes import Quote, ProcessQuotes, main


# ── Sample data ──────────────────────────────────────────────────────────────

SAMPLE_MD = """*quote:*	Yeah Matt Damon saying "fortune favours the bold" certainly didn't favour SBF's victims.
*source:*	reddit r/perth
*author:*	Captain-Peacock
*link:*	https://www.reddit.com/r/perth/comments/zlcc45/gamblers_anonymous_warns_of_really_really_sad/j053yug/
*note:*

*quote:*	I felt overwhelmed by stimuli from within: thoughts.
*source:*	But You Dont Look Autistic
*author:*	Bianca Toeps
*link:*
*note:*	If autism is a sensory processing disorder, maybe adhd is just autism specifically for thoughts?

*quote:*	A more inclusive, more comprehensive explanation can be found in the Intense World Theory, a theory that has been gaining more credence in the past few years. The founders of this theory, neuroscientists Henry and Kamila Markram, have an autistic son.
*source:*	But You Dont Look Autistic
*author:*	Bianca Toeps
*link:*
*note:*
"""

SAMPLE_HEADER = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <div class="tableOfContentsDiv">
        <!-- table of contents -->
    </div>
    <div class="quotesDiv">
        <!--quotes-->
    </div>
</body>
</html>"""


# ── Quote class tests ────────────────────────────────────────────────────────


class TestQuote:
    def test_empty_quote_has_empty_title(self):
        q = Quote()
        q.quote = ""
        q.generate_title()
        assert q.title == ""

    def test_short_quote_uses_full_text(self):
        q = Quote()
        q.quote = "Hello world"
        q.generate_title()
        assert q.title == "Hello world"

    def test_short_quote_exactly_seven_words(self):
        q = Quote()
        q.quote = "one two three four five six seven"
        q.generate_title()
        assert q.title == "one two three four five six seven"

    def test_short_quote_exactly_eight_words(self):
        q = Quote()
        q.quote = "one two three four five six seven eight"
        q.generate_title()
        assert q.title == "one two three four five six seven eight"

    def test_long_quote_truncates_to_eight_words(self):
        q = Quote()
        q.quote = "one two three four five six seven eight nine ten"
        q.generate_title()
        assert q.title == "one two three four five six seven eight..."

    def test_quote_has_random_id(self):
        q1 = Quote()
        q2 = Quote()
        assert q1.id_for_quote != q2.id_for_quote


# ── ProcessQuotes parsing tests ──────────────────────────────────────────────


class TestProcessQuotes:
    def test_parses_multiple_quotes(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        assert len(pq.quotes) == 3

    def test_parses_quote_text(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        q = pq.quotes[0]
        assert "fortune favours the bold" in q.quote
        assert "SBF's victims" in q.quote

    def test_parses_source(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        assert pq.quotes[0].source == "reddit r/perth"

    def test_parses_author(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        assert pq.quotes[0].author == "Captain-Peacock"

    def test_parses_link(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        assert "reddit.com" in pq.quotes[0].link

    def test_parses_note(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        assert pq.quotes[1].note == (
            "If autism is a sensory processing disorder,"
            " maybe adhd is just autism specifically for thoughts?"
        )

    def test_empty_note_becomes_empty_string(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        assert pq.quotes[2].note == ""

    def test_generates_titles_for_all_quotes(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        titles = [q.title for q in pq.quotes]
        assert len(titles) == 3
        assert all(t != "" for t in titles)

    def test_quote_titles_dict_populated(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        assert len(pq.quote_titles) == 3


# ── HTML output tests (no file IO) ──────────────────────────────────────────


class TestHtmlGeneration:
    def test_write_quote_attribute_to_file_basic_div_structure(self):
        """Each quote div has the expected class and id."""
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.render_quote_html(pq.quotes[0])
        assert '<div class="quote"' in html
        assert f'id="{pq.quotes[0].id_for_quote}"' in html
        assert "</div>" in html

    def test_write_quote_contains_title(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.render_quote_html(pq.quotes[0])
        assert '<p class="quote-title">' in html

    def test_write_quote_contains_source_tagged(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.render_quote_html(pq.quotes[0])
        assert '<span class="source-source">Source:</span>' in html
        assert "reddit r/perth" in html

    def test_write_quote_contains_author_tagged(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.render_quote_html(pq.quotes[0])
        assert '<span class="tag-author">Author:</span>' in html
        assert "Captain-Peacock" in html

    def test_write_quote_contains_link_tagged(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.render_quote_html(pq.quotes[0])
        assert '<span class="tag-link">Link:</span>' in html
        assert "reddit.com" in html

    def test_write_quote_contains_note_tagged(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.render_quote_html(pq.quotes[1])
        assert '<p class="note">' in html
        assert "sensory processing" in html

    def test_generateHtml_injects_table_of_contents(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.generate_html(header_template=SAMPLE_HEADER)
        assert '<div class="table-of-contents">' in html
        assert '<a class="tableOfContents"' in html

    def test_generateHtml_injects_quotes(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.generate_html(header_template=SAMPLE_HEADER)
        assert '<div class="quote"' in html
        assert "fortune favours the bold" in html

    def test_generateHtml_replaces_all_placeholders(self):
        """No raw template markers should remain in the output."""
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.generate_html(header_template=SAMPLE_HEADER)
        assert "<!-- table of contents -->" not in html
        assert "<!--quotes-->" not in html

    def test_generateHtml_contains_doctype(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        html = pq.generate_html(header_template=SAMPLE_HEADER)
        assert html.startswith("<!DOCTYPE html>")


# ── addClassToTD tests ──────────────────────────────────────────────────────


class TestAddClassToTD:
    def test_adds_classes_to_th(self):
        pq = ProcessQuotes("")
        table = "<table><tr><th>title</th><th>source</th></tr></table>"
        result = pq._add_column_classes(table)
        assert 'class="column0"' in result

    def test_adds_classes_to_td(self):
        pq = ProcessQuotes("")
        # The function works line-by-line, matching real pandas output.
        # Each <td> must be on its own line for proper column counting.
        table = "<table>\n<tr>\n<td>Hello</td>\n<td>World</td>\n</tr>\n</table>"
        result = pq._add_column_classes(table)
        assert 'class="column0"' in result
        assert 'class="column1"' in result


# ── Table of contents tests ─────────────────────────────────────────────────


class TestTableOfContents:
    def test_toc_has_div_wrapper(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        toc = pq.render_toc()
        assert toc.startswith('<div class="table-of-contents">')
        assert toc.strip().endswith("</div>")

    def test_toc_contains_links(self):
        pq = ProcessQuotes(SAMPLE_MD).parse_quotes()
        toc = pq.render_toc()
        for quote in pq.quotes:
            assert f'href="#{quote.id_for_quote}"' in toc


# ── main() integration tests (tmp_path avoids real filesystem pollution) ────


class TestMainFunction:
    def test_main_writes_html_file(self, tmp_path: Path):
        """main() reads a .md input and writes the expected output file."""
        input_md = tmp_path / "input.md"
        input_md.write_text(SAMPLE_MD, encoding="utf-8")

        header_html = tmp_path / "Header.html"
        header_html.write_text(SAMPLE_HEADER, encoding="utf-8")

        output_html = tmp_path / "output.html"

        # Temporarily chdir so that writeQuotes can find Header.html
        original_cwd = Path.cwd()
        try:
            __import__("os").chdir(tmp_path)
            main(quotes_input=input_md, output_html=output_html)
        finally:
            __import__("os").chdir(str(original_cwd))

        assert output_html.exists()
        content = output_html.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "fortune favours the bold" in content
        assert '<div class="table-of-contents">' in content

    def test_main_default_output(self, tmp_path: Path):
        """main() writes to index.html by default."""
        input_md = tmp_path / "input.md"
        input_md.write_text(SAMPLE_MD, encoding="utf-8")

        header_html = tmp_path / "Header.html"
        header_html.write_text(SAMPLE_HEADER, encoding="utf-8")

        original_cwd = Path.cwd()
        try:
            __import__("os").chdir(tmp_path)
            main(quotes_input=input_md)
        finally:
            __import__("os").chdir(str(original_cwd))

        assert (tmp_path / "index.html").exists()


# ── Argparse / CLI tests ────────────────────────────────────────────────────


class TestCliArgparse:
    def test_argparse_accepts_md_file(self):
        """The argument parser accepts a --quotes_input with .md suffix."""
        from scripts.processQuotes import parser as cli_parser

        args = cli_parser.parse_args(["--quotes_input", "test.md"])
        assert args.quotes_input == "test.md"

    def test_argparse_defaults(self):
        """Default values are set for both arguments."""
        from scripts.processQuotes import parser as cli_parser

        args = cli_parser.parse_args([])
        assert args.quotes_input == "markdown_quotes/QuotesProcessed.md"
        assert args.output_html == "index.html"

    def test_argparse_custom_output(self):
        from scripts.processQuotes import parser as cli_parser

        args = cli_parser.parse_args([
            "--quotes_input",
            "in.md",
            "--output-html",
            "out.html",
        ])
        assert args.quotes_input == "in.md"
        assert args.output_html == "out.html"
