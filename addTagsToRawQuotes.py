"""
Add tags to raw quotes to produce a semi-processed markdown file.

Takes a raw quotes file (markdown_quotes/sampleQuotesUnprocessed.md by default) and structures
each quote block into tagged fields: *quote:*, *source:*, *author:*, *link:*, *note:*.

The output is meant to be manually curated before feeding into processQuotes.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

# Known authors — handled case-insensitively, then titlecased in output
KNOWN_AUTHORS: List[str] = [
    "tim low",
    "david foster wallace",
    "steve silberman",
    "jennifer doudna",
    "mark twain",
    "charles darwin",
    "alastair reynolds",
    "adam rutherford",
    "david quammen",
    "sam harris",
]


def _normalise_authors() -> dict:
    """Return a dict mapping lowercase author names to titlecase versions."""
    return {a.lower(): a.title() for a in KNOWN_AUTHORS}


def _detect_author(text: str, author_map: dict) -> str:
    """Return the titlecased author name if found in text, else empty string."""
    for lower_name, title_name in author_map.items():
        if lower_name in text.lower():
            return title_name
    return ""


def _write_quote(
    quote_text: str,
    source_text: str,
    author_text: str,
    link_text: str,
    note_text: str,
) -> str:
    """Format a single quote into the tagged output string."""
    lines = [
        f"*quote:*\t{quote_text}",
        f"*source:*\t{source_text}",
        f"*author:*\t{author_text}",
        f"*link:*\t{link_text}",
        f"*note:*\t{note_text}",
        "",  # blank line between quotes
    ]
    return "\n".join(lines)


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
    Lines within each quote are assumed to be in order:
        1. quote text
        2. source
        3. note

    iOS-copied quotes (containing 'Excerpt from') are handled differently
    to extract source from after that marker.

    Links are identified by the presence of 'http' in a line.

    Returns the tagged output as a string.
    """
    author_map = _normalise_authors()
    output_parts: list[str] = []

    for raw_block in raw_quote_text.split("*quote*"):
        quote = raw_block.strip()
        if not quote:
            continue

        lines = quote.splitlines()
        # Remove empty lines
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


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Add tags to raw quotes to produce a semi-processed markdown file.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        default="markdown_quotes/sampleQuotesUnprocessed.md",
        help="Path to the raw quotes markdown file (default: markdown_quotes/sampleQuotesUnprocessed.md).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="markdown_quotes/sampleQuotesSemiProcessed.md",
        help="Path for the output semi-processed markdown file (default: markdown_quotes/sampleQuotesSemiProcessed.md).",
    )
    return parser


def argparse_entrypoint() -> None:
    """
    Argparse entrypoint function to be run when __name__ == '__main__'.

    Parses CLI arguments and calls quote_handler to process the file.
    """
    parser = _build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")

    quote_handler(
        unprocessed_quotes=args.input,
        output_file=args.output,
    )


if __name__ == "__main__":
    argparse_entrypoint()
