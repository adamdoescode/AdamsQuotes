"""
Pipeline stage 1: raw quotes → semi-processed tagged markdown.

Migrated from ``addTagsToRawQuotes.py``.  Uses ``format_tagged_quote`` from
:mod:`adamsquotes.text_utils` for the output format.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from adamsquotes.text_utils import (
    _normalise_authors,
    _detect_author,
    format_tagged_quote,
)


# Note: KNOWN_AUTHORS is now in adamsquotes.types — used via _normalise_authors()


def _write_quote(
    quote_text: str,
    source_text: str,
    author_text: str,
    link_text: str,
    note_text: str,
) -> str:
    """Format a single quote into the tagged output string."""
    return format_tagged_quote(
        quote_text, source_text, author_text, link_text, note_text, clean=False
    )


def _process_ios_quote(lines: list[str], author_map: dict) -> dict:
    """Process a quote block that originated from an iOS copy (contains 'Excerpt from')."""
    fields = {"quote": "", "source": "", "note": "", "link": "", "author": ""}

    full_text = "\n".join(lines)
    fields["author"] = _detect_author(full_text, author_map)

    next_line_is_source = False
    for count, line in enumerate(lines):
        line = line.strip()
        if count == 0:
            fields["quote"] = line
        if "excerpt from" in line.lower():
            next_line_is_source = True
        elif next_line_is_source:
            fields["source"] = line
            next_line_is_source = False
        if "http" in line:
            fields["link"] = line

    return fields


def _process_normal_quote(lines: list[str], author_map: dict) -> dict:
    """Process a standard quote block where order is: quote, source, note."""
    fields = {"quote": "", "source": "", "note": "", "link": "", "author": ""}

    for count, line in enumerate(lines):
        line = line.strip()
        if len(line) == 0:
            break
        if count == 0:
            fields["quote"] = line
        elif count == 1:
            fields["source"] = line
        elif count == 2:
            fields["note"] = line
        if "http" in line:
            fields["link"] = line

    full_text = "\n".join(lines)
    detected_author = _detect_author(full_text, author_map)
    if detected_author:
        fields["author"] = detected_author
        # Strip author name from source if it was embedded there
        fields["source"] = fields["source"].replace(detected_author, "").strip()

    return fields


def process_raw_quotes(raw_quote_text: str) -> str:
    """
    Take raw markdown quote text and structure it with tags.

    Raw quotes are separated by '*quote*' (no colon).
    Lines within each quote are assumed to be in order: quote text, source, note.

    Returns the tagged output as a string.
    """
    author_map = _normalise_authors()
    output_parts: list[str] = []

    for raw_block in raw_quote_text.split("*quote*"):
        quote = raw_block.strip()
        if not quote:
            continue

        lines = quote.splitlines()
        lines = [line for line in lines if len(line.strip()) > 0]
        if not lines:
            continue

        is_ios = "excerpt" in quote.lower()
        if is_ios:
            fields = _process_ios_quote(lines, author_map)
        else:
            fields = _process_normal_quote(lines, author_map)

        if fields["quote"]:
            output_parts.append(
                _write_quote(
                    fields["quote"],
                    fields["source"],
                    fields["author"],
                    fields["link"],
                    fields["note"],
                )
            )

    return "\n".join(output_parts)


def quote_handler(
    unprocessed_quotes: str | Path = "markdown_quotes/sampleQuotesUnprocessed.md",
    output_file: str | Path = "markdown_quotes/sampleQuotesSemiProcessed.md",
) -> None:
    """
    Read raw quotes from a file, process them, and write the tagged output.

    Args:
        unprocessed_quotes: Path to the input raw markdown file.
        output_file: Path for the output semi-processed markdown file.
    """
    input_path = Path(unprocessed_quotes)
    output_path = Path(output_file)

    raw_text = input_path.read_text(encoding="utf-8")
    tagged_output = process_raw_quotes(raw_text)
    output_path.write_text(tagged_output, encoding="utf-8")

    print(f"Processed: {input_path} -> {output_path}")
