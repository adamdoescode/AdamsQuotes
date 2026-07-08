"""
CLI entry point for the tagger stage (raw quotes → semi-processed tagged markdown).

Usage::

    uv run python -m adamsquotes.cli.tagger
    uv run python -m adamsquotes.cli.tagger my_quotes.md -o output.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

from adamsquotes.types import DEFAULT_RAW_INPUT, DEFAULT_SEMI_OUTPUT


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Add tags to raw quotes to produce a semi-processed markdown file.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        default=DEFAULT_RAW_INPUT,
        help=(
            f"Path to the raw quotes markdown file "
            f"(default: {DEFAULT_RAW_INPUT})."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_SEMI_OUTPUT,
        help=(
            f"Path for the output semi-processed markdown file "
            f"(default: {DEFAULT_SEMI_OUTPUT})."
        ),
    )
    return parser


def main() -> None:
    """Parse CLI args and run the tagger pipeline."""
    parser = _build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")

    # Defer import so the pipeline module doesn't need to be loaded at parse time
    from adamsquotes.pipeline.tagger import quote_handler  # noqa: PLC0415

    quote_handler(
        unprocessed_quotes=args.input,
        output_file=args.output,
    )


if __name__ == "__main__":
    main()