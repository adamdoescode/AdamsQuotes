"""
Tests for text processing utilities in adamsquotes.text_utils.
"""

from __future__ import annotations

from adamsquotes.text_utils import (
    _is_url,
    _contains_url,
    _clean_text,
    _unwrap_paragraphs,
    _is_dash_line,
    _is_italic_marker,
    _is_title_like,
    _ends_with_sentence_punct,
    format_tagged_quote,
    _normalise_authors,
    _detect_author,
)


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


class TestIsUrl:
    def test_bare_http_url(self):
        assert _is_url("http://example.com") is True

    def test_bare_https_url(self):
        assert _is_url("https://example.com/path") is True

    def test_url_with_angle_brackets(self):
        assert _is_url("<https://example.com>") is True

    def test_not_a_url(self):
        assert _is_url("just some text") is False

    def test_empty_string(self):
        assert _is_url("") is False


class TestContainsUrl:
    def test_extracts_url_from_text(self):
        url = _contains_url("see https://example.com for more")
        assert url == "https://example.com"

    def test_no_url_returns_none(self):
        assert _contains_url("just text") is None

    def test_multiple_urls_first_is_returned(self):
        url = _contains_url("a https://first.com b https://second.com")
        assert url == "https://first.com"


class TestCleanText:
    def test_removes_backslash_quote(self):
        assert _clean_text(r"it\'s") == "it's"

    def test_removes_backslash_double_quote(self):
        assert _clean_text(r'he said \"hello\"') == 'he said "hello"'

    def test_removes_backslash_dash(self):
        assert _clean_text(r"long\--dash") == "long--dash"

    def test_no_escapes_unchanged(self):
        assert _clean_text("normal text") == "normal text"


class TestUnwrapParagraphs:
    def test_joins_hard_wrapped_lines(self):
        text = "This is a\nhard wrapped\nparagraph."
        result = _unwrap_paragraphs(text)
        assert result == "This is a hard wrapped paragraph."

    def test_preserves_blank_line_breaks(self):
        text = "First paragraph.\n\nSecond paragraph."
        result = _unwrap_paragraphs(text)
        assert result == "First paragraph.\n\nSecond paragraph."

    def test_single_line_unchanged(self):
        assert _unwrap_paragraphs("Hello world") == "Hello world"


class TestIsDashLine:
    def test_dash_line_true(self):
        assert _is_dash_line("----------") is True

    def test_short_line_false(self):
        assert _is_dash_line("--") is False

    def test_non_dash_line_false(self):
        assert _is_dash_line("Hello world") is False


class TestIsItalicMarker:
    def test_italic_marker_true(self):
        assert _is_italic_marker("*Book Title*") is True

    def test_short_marker_false(self):
        assert _is_italic_marker("*ab*") is False

    def test_no_asterisks_false(self):
        assert _is_italic_marker("Book Title") is False


class TestIsTitleLike:
    def test_title_like_true(self):
        assert _is_title_like("Voyage of the Beagle") is True

    def test_sentence_punctuation_false(self):
        assert _is_title_like("This is a sentence.") is False

    def test_too_long_false(self):
        assert _is_title_like("A" * 61) is False


class TestEndsWithSentencePunct:
    def test_ends_with_period(self):
        assert _ends_with_sentence_punct("Hello world.") is True

    def test_ends_with_question_mark(self):
        assert _ends_with_sentence_punct("Hello world?") is True

    def test_no_punctuation(self):
        assert _ends_with_sentence_punct("Hello world") is False

    def test_common_abbreviation(self):
        assert _ends_with_sentence_punct("see vol.") is False

    def test_numeric_suffix(self):
        assert _ends_with_sentence_punct("chapter 5.") is False


class TestFormatTaggedQuote:
    def test_basic_format(self):
        result = format_tagged_quote("Hello", "Source", "", "", "", clean=False)
        assert "*quote:*\tHello" in result
        assert "*source:*\tSource" in result
        assert "*author:*\t" in result
        assert "*link:*\t" in result
        assert "*note:*\t" in result

    def test_trailing_newline(self):
        result = format_tagged_quote("A", "B", "C", "D", "E", clean=False)
        assert result.endswith("\n")

    def test_clean_applies_text_cleaning(self):
        input_text = r"it\'s a test"
        result = format_tagged_quote(input_text, "source", "", "", "", clean=True)
        assert "it's" in result