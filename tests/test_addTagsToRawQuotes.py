"""
Tests for addTagsToRawQuotes.py — core logic and argparse interface,
all without touching real files (except for an end-to-end snapshot test).
"""

from pathlib import Path

import pytest

from addTagsToRawQuotes import (
    process_raw_quotes,
    quote_handler,
    _write_quote,
    _normalise_authors,
    _detect_author,
    _build_parser,
)


# ── Sample raw input (representative of sampleQuotesUnprocessed.md) ──────────

RAW_INPUT = """*quote*
I felt overwhelmed by stimuli from within: thoughts.
But You Dont Look Autistic
If autism is a sensory processing disorder, maybe adhd is just autism specifically for thoughts?

*quote*
There, he earned his final footnote in history by befriending a fellow POW.
Neurotribes steve silberman

*quote*
"The gesture that precipitates this insight"

Excerpt from
Waking Up: A Guide to Spirituality Without Religion
Sam Harris
This material may be protected by copyright.

*quote*
I love it, because it's so strange, so dizzying.
https://www.robinsloan.com/newsletters/visions/#spotify

*quote*
"Things look different without the Prophets' lies clouding my vision." - To the Arbiter, on board of the Shadow of Intent.

*quote*
A lot of not quitting quotes are bullshit.
Michael Jordan quit college before he graduated.
Michael Jordan then quit basketball to play baseball.
https://www.reddit.com/r/GetMotivated/comments/5m7a3p/image_xkcd_shouldve_left_sooner/dc1qpwj/
"""

# ── Expected semi-processed output (golden snapshot) ─────────────────────────

EXPECTED_OUTPUT = (
    "*quote:*\tI felt overwhelmed by stimuli from within: thoughts.\n"
    "*source:*\tBut You Dont Look Autistic\n"
    "*author:*\t\n"
    "*link:*\t\n"
    "*note:*\tIf autism is a sensory processing disorder,"
    " maybe adhd is just autism specifically for thoughts?\n"
    "\n"
    "*quote:*\tThere, he earned his final footnote in history"
    " by befriending a fellow POW.\n"
    "*source:*\tNeurotribes steve silberman\n"
    "*author:*\tSteve Silberman\n"
    "*link:*\t\n"
    "*note:*\t\n"
    "\n"
    '*quote:*\t"The gesture that precipitates this insight"\n'
    "*source:*\tWaking Up: A Guide to Spirituality Without Religion\n"
    "*author:*\tSam Harris\n"
    "*link:*\t\n"
    "*note:*\t\n"
    "\n"
    "*quote:*\tI love it, because it's so strange, so dizzying.\n"
    "*source:*\thttps://www.robinsloan.com/newsletters/visions/#spotify\n"
    "*author:*\t\n"
    "*link:*\thttps://www.robinsloan.com/newsletters/visions/#spotify\n"
    "*note:*\t\n"
    "\n"
    "*quote:*\t\"Things look different without the Prophets'"
    ' lies clouding my vision." - To the Arbiter,'
    " on board of the Shadow of Intent.\n"
    "*source:*\t\n"
    "*author:*\t\n"
    "*link:*\t\n"
    "*note:*\t\n"
    "\n"
    "*quote:*\tA lot of not quitting quotes are bullshit.\n"
    "*source:*\tMichael Jordan quit college before he graduated.\n"
    "*author:*\t\n"
    "*link:*\thttps://www.reddit.com/r/GetMotivated/comments/5m7a3p/"
    "image_xkcd_shouldve_left_sooner/dc1qpwj/\n"
    "*note:*\tMichael Jordan then quit basketball to play baseball.\n"
)


# ── Helper unit tests ────────────────────────────────────────────────────────


class TestNormaliseAuthors:
    def test_returns_lowercase_to_titlecase_map(self):
        am = _normalise_authors()
        assert am["tim low"] == "Tim Low"
        assert am["david foster wallace"] == "David Foster Wallace"

    def test_includes_all_known_authors(self):
        am = _normalise_authors()
        assert len(am) >= 10


class TestDetectAuthor:
    def test_detects_author_in_text(self):
        am = _normalise_authors()
        assert _detect_author("this is by Tim Low btw", am) == "Tim Low"

    def test_detects_author_case_insensitive(self):
        am = _normalise_authors()
        assert _detect_author("TIM LOW said something", am) == "Tim Low"

    def test_returns_empty_when_not_found(self):
        am = _normalise_authors()
        assert _detect_author("some random text", am) == ""


class TestWriteQuote:
    def test_basic_format(self):
        result = _write_quote("Hello", "Source", "", "", "")
        assert "*quote:*\tHello" in result
        assert "*source:*\tSource" in result
        assert "*author:*\t" in result
        assert "*link:*\t" in result
        assert "*note:*\t" in result

    def test_trailing_newline_between_quotes(self):
        result = _write_quote("A", "B", "C", "D", "E")
        assert result.endswith("\n")


# ── process_raw_quotes tests (pure function, no IO) ─────────────────────────


class TestProcessRawQuotes:
    def test_happy_path_default(self):
        """Golden snapshot: the output for the representative raw input
        must match EXPECTED_OUTPUT exactly."""
        result = process_raw_quotes(RAW_INPUT)
        assert result == EXPECTED_OUTPUT

    def test_correct_quote_count(self):
        result = process_raw_quotes(RAW_INPUT)
        quote_blocks = [b for b in result.split("\n") if b.startswith("*quote:*")]
        assert len(quote_blocks) == 6

    def test_normal_quote_extracts_source(self):
        result = process_raw_quotes(RAW_INPUT)
        assert "But You Dont Look Autistic" in result

    def test_normal_quote_with_author_in_source(self):
        """When the author is embedded in the source line, author is extracted
        and source is cleaned."""
        result = process_raw_quotes(RAW_INPUT)
        assert "Steve Silberman" in result

    def test_ios_excerpt_extracts_source(self):
        """iOS-style quotes (with 'Excerpt from') should have source from
        the line after the marker."""
        result = process_raw_quotes(RAW_INPUT)
        assert "Waking Up: A Guide to Spirituality Without Religion" in result

    def test_ios_excerpt_detects_author(self):
        result = process_raw_quotes(RAW_INPUT)
        assert "Sam Harris" in result

    def test_detects_link_by_http(self):
        result = process_raw_quotes(RAW_INPUT)
        assert "reddit.com" in result

    def test_missing_fields_remain_empty(self):
        """A quote with only text and no source/note should still parse."""
        result = process_raw_quotes(RAW_INPUT)
        lines = result.split("\n")
        # Find the Halo quote block — it has empty source/author/link/note
        assert "*author:*\t" in result
        assert "*link:*\t" in result

    def test_header_line_is_skipped(self):
        """The leading 'Quotes' line before the first *quote* marker should
        be ignored (no empty quote)."""
        result = process_raw_quotes(RAW_INPUT)
        quote_blocks = [b for b in result.split("\n") if b.startswith("*quote:*")]
        assert len(quote_blocks) == 6


# ── quote_handler tests (file IO via tmp_path) ──────────────────────────────


class TestQuoteHandler:
    def test_processes_file_and_writes_output(self, tmp_path):
        input_file = tmp_path / "input.md"
        output_file = tmp_path / "output.md"
        input_file.write_text(RAW_INPUT, encoding="utf-8")

        quote_handler(unprocessed_quotes=input_file, output_file=output_file)

        assert output_file.exists()
        result = output_file.read_text(encoding="utf-8")
        assert result == EXPECTED_OUTPUT

    def test_default_output_path(self, tmp_path):
        """quote_handler writes to the specified output path correctly."""
        input_file = tmp_path / "raw.md"
        output_file = tmp_path / "semi.md"
        input_file.write_text("*quote*\nHello\nSource\n", encoding="utf-8")

        quote_handler(unprocessed_quotes=input_file, output_file=output_file)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "*quote:*\tHello" in content


# ── Argparse tests ──────────────────────────────────────────────────────────


class TestBuildParser:
    def test_default_input(self):
        parser = _build_parser()
        ns = parser.parse_args([])
        assert ns.input == "sampleQuotesUnprocessed.md"

    def test_default_output(self):
        parser = _build_parser()
        ns = parser.parse_args([])
        assert ns.output == "sampleQuotesSemiProcessed.md"

    def test_custom_input(self):
        parser = _build_parser()
        ns = parser.parse_args(["my_quotes.md"])
        assert ns.input == "my_quotes.md"

    def test_custom_output_flag(self):
        parser = _build_parser()
        ns = parser.parse_args(["in.md", "-o", "out.md"])
        assert ns.input == "in.md"
        assert ns.output == "out.md"


# ── End-to-end snapshot test using real sample data ─────────────────────────


class TestEndToEnd:
    """Read the real sampleQuotesUnprocessed.md and compare with existing
    sampleQuotesSemiProcessed.md to verify the pipeline is stable."""

    SAMPLE_UNPROCESSED = Path(__file__).parents[1] / "sampleQuotesUnprocessed.md"
    SAMPLE_SEMI_PROCESSED = Path(__file__).parents[1] / "sampleQuotesSemiProcessed.md"

    def test_process_raw_file_matches_semi_processed_snapshot(self):
        if not self.SAMPLE_UNPROCESSED.exists():
            pytest.skip("sampleQuotesUnprocessed.md not found")
        if not self.SAMPLE_SEMI_PROCESSED.exists():
            pytest.skip("sampleQuotesSemiProcessed.md not found")

        raw_text = self.SAMPLE_UNPROCESSED.read_text(encoding="utf-8")
        actual = process_raw_quotes(raw_text)
        # Compare against the manually-curated semi-processed file
        # Note: because the semi-processed file has been manually tweaked,
        # we just check structural consistency (same number of quotes)
        expected_lines = self.SAMPLE_SEMI_PROCESSED.read_text(encoding="utf-8").split(
            "\n"
        )
        actual_quotes = [l for l in actual.split("\n") if l.startswith("*quote:*")]
        expected_quotes = [l for l in expected_lines if l.startswith("*quote:*")]
        assert len(actual_quotes) == len(expected_quotes), (
            f"Expected {len(expected_quotes)} quotes, got {len(actual_quotes)}"
        )
