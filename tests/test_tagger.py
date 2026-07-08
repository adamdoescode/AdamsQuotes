"""
Tests for the tagger pipeline (adamsquotes.pipeline.tagger).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adamsquotes.pipeline.tagger import process_raw_quotes, quote_handler
from tests.conftest import RAW_INPUT, EXPECTED_OUTPUT


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
        result = process_raw_quotes(RAW_INPUT)
        assert "Steve Silberman" in result

    def test_ios_excerpt_extracts_source(self):
        result = process_raw_quotes(RAW_INPUT)
        assert "Waking Up: A Guide to Spirituality Without Religion" in result

    def test_ios_excerpt_detects_author(self):
        result = process_raw_quotes(RAW_INPUT)
        assert "Sam Harris" in result

    def test_detects_link_by_http(self):
        result = process_raw_quotes(RAW_INPUT)
        assert "reddit.com" in result

    def test_missing_fields_remain_empty(self):
        result = process_raw_quotes(RAW_INPUT)
        assert "*author:*\t" in result
        assert "*link:*\t" in result

    def test_header_line_is_skipped(self):
        result = process_raw_quotes(RAW_INPUT)
        quote_blocks = [b for b in result.split("\n") if b.startswith("*quote:*")]
        assert len(quote_blocks) == 6


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
        input_file = tmp_path / "raw.md"
        output_file = tmp_path / "semi.md"
        input_file.write_text("*quote*\nHello\nSource\n", encoding="utf-8")

        quote_handler(unprocessed_quotes=input_file, output_file=output_file)

        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "*quote:*\tHello" in content
