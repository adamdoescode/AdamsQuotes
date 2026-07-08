"""
Backward-compatible wrapper.  Delegates to ``adamsquotes.pipeline.converter``.

Usage::

    uv run python processNewQuotes.py
    uv run python processNewQuotes.py path/to/input.md -o path/to/output.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

from adamsquotes.pipeline.converter import (
    process_file as process_file,
    split_blocks as split_blocks,
)
from adamsquotes.text_utils import (
    _is_url as _is_url,
    _contains_url as _contains_url,
    _clean_text as _clean_text,
    _unwrap_paragraphs as _unwrap_paragraphs,
    _is_dash_line as _is_dash_line,
    _is_italic_marker as _is_italic_marker,
    _is_title_like as _is_title_like,
    _ends_with_sentence_punct as _ends_with_sentence_punct,
    format_tagged_quote,
)

_build_quote_output = format_tagged_quote


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Process new_quotes_unprocessed.md format into tagged output.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        default="markdown_quotes/new_quotes_unprocessed.md",
        help="Path to the raw quotes markdown file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="markdown_quotes/new_quotes_tagged.md",
        help="Path for the output tagged markdown file.",
    )
    return parser


def main() -> None:
    """Parse CLI args and run the converter."""
    parser = _build_parser()
    args = parser.parse_args()
    input_path = Path(args.input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")
    process_file(input_path, Path(args.output))


if __name__ == "__main__":
    main()
