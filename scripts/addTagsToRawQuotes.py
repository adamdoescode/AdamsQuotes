"""
Backward-compatible wrapper.  Delegates to ``adamsquotes.pipeline.tagger``.

Usage::

    uv run python addTagsToRawQuotes.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from adamsquotes.pipeline.tagger import (
    process_raw_quotes as process_raw_quotes,
    quote_handler as quote_handler,
)
from adamsquotes.text_utils import (
    _normalise_authors as _normalise_authors,
    _detect_author as _detect_author,
)
from adamsquotes.text_utils import format_tagged_quote


_write_quote = format_tagged_quote
KNOWN_AUTHORS = None  # replaced by adamsquotes.types.KNOWN_AUTHORS


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
