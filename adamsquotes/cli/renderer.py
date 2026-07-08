"""
CLI entry point for the renderer stage (tagged markdown → styled HTML).

Usage::

    uv run python -m adamsquotes.cli.renderer
    uv run python -m adamsquotes.cli.renderer --quotes_input my_quotes.md --output-html out.html
"""

from __future__ import annotations

import argparse
from pathlib import Path

from adamsquotes.types import DEFAULT_PROCESSED_INPUT, DEFAULT_HTML_OUTPUT


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Process a markdown quotes file into an HTML file.",
    )
    parser.add_argument(
        "--quotes_input",
        type=str,
        default=DEFAULT_PROCESSED_INPUT,
        help="Path to the input markdown file (must have .md suffix).",
    )
    parser.add_argument(
        "--output-html",
        type=str,
        default=DEFAULT_HTML_OUTPUT,
        help=f"Path for the output HTML file (default: {DEFAULT_HTML_OUTPUT}).",
    )
    return parser


def main() -> None:
    """Parse CLI args and run the renderer pipeline."""
    parser = _build_parser()
    args = parser.parse_args()

    input_path = Path(args.quotes_input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")

    from adamsquotes.pipeline.html_renderer import (  # noqa: PLC0415
        parse_quotes,
        write_html,
    )

    text = input_path.read_text(encoding="utf-8")
    quotes = parse_quotes(text)
    write_html(quotes, output_path=args.output_html)


if __name__ == "__main__":
    main()
