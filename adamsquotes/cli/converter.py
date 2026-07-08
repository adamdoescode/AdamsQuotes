"""
CLI entry point for the converter stage (new-format quotes → tagged markdown).

Usage::

    uv run python -m adamsquotes.cli.converter
    uv run python -m adamsquotes.cli.converter path/to/input.md -o output.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

from adamsquotes.types import DEFAULT_NEW_INPUT, DEFAULT_NEW_OUTPUT


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Process new-format raw quotes into tagged output.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        default=DEFAULT_NEW_INPUT,
        help=f"Path to the raw quotes markdown file (default: {DEFAULT_NEW_INPUT}).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=DEFAULT_NEW_OUTPUT,
        help=f"Path for the output tagged markdown file (default: {DEFAULT_NEW_OUTPUT}).",
    )
    return parser


def main() -> None:
    """Parse CLI args and run the converter pipeline."""
    parser = _build_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")

    from adamsquotes.pipeline.converter import process_file  # noqa: PLC0415

    process_file(input_path, Path(args.output))


if __name__ == "__main__":
    main()
