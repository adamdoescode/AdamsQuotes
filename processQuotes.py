"""
Process tagged markdown quotes into a styled HTML page.

Backward-compatible wrapper that delegates to the new ``adamsquotes.pipeline.html_renderer``
module. All new code should import from there directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict
import argparse

from adamsquotes.models import Quote as _Quote
from adamsquotes.pipeline import html_renderer as _renderer


class Quote(_Quote):
    """A single quote with metadata. Replaced by ``adamsquotes.models.Quote``."""

    def generate_title(self) -> "Quote":
        super().generate_title()
        return self


class ProcessQuotes:
    """Parse tagged markdown and produce HTML.

    Wraps the module-level functions from ``adamsquotes.pipeline.html_renderer``
    for backward compatibility.
    """

    def __init__(self, quotes: str):
        self.raw_text: str = quotes
        self.quotes: List[Quote] = []
        self.quote_titles: Dict[str, int] = {}

    def _register_title(self, quote: Quote) -> "ProcessQuotes":
        self.quote_titles[quote.title] = quote.id_for_quote
        return self

    def _add_column_classes(self, table: str) -> str:
        return _renderer._add_column_classes(table)

    def render_toc(self) -> str:
        if not self.quotes:
            self.parse_quotes()
        return _renderer.render_toc(self.quotes)

    def parse_quotes(self) -> "ProcessQuotes":
        self.quotes = _renderer.parse_quotes(self.raw_text)
        for q in self.quotes:
            self._register_title(q)
        return self

    def print_quotes(self, num_quotes: int | None = None) -> None:
        counter = 0
        for quote in self.quotes:
            if num_quotes is not None and counter >= num_quotes:
                break
            print(f"quote: {quote.quote}")
            print(f"source: {quote.source}")
            print(f"note: {quote.note}")
            print(f"id: {quote.id_for_quote}")
            print()
            counter += 1

    def render_quote_html(self, quote: Quote) -> str:
        return _renderer.render_quote_html(quote)

    def generate_html(self, header_template: str) -> str:
        if not self.quotes:
            self.parse_quotes()
        return _renderer.generate_html(self.quotes, header_template)

    def write_html(self, output_path: str | Path = "index.html") -> None:
        if not self.quotes:
            self.parse_quotes()
        _renderer.write_html(self.quotes, output_path=output_path)


def main(quotes_input: str | Path, output_html: str | Path = "index.html") -> None:
    """
    Process a markdown file of quotes and write the result to an HTML file.

    Args:
        quotes_input: Path to the input markdown file (must have .md suffix).
        output_html: Path for the output HTML file (defaults to 'index.html').
    """
    quotes_path = Path(quotes_input)
    output_path = Path(output_html)
    quotes = quotes_path.read_text(encoding="utf-8")
    processed = ProcessQuotes(quotes).parse_quotes()
    processed.write_html(output_path)


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Process a markdown quotes file into an HTML file."
    )
    parser.add_argument(
        "--quotes_input",
        type=str,
        default="markdown_quotes/QuotesProcessed.md",
        help="Path to the input markdown file (must have .md suffix).",
    )
    parser.add_argument(
        "--output-html",
        type=str,
        default="index.html",
        help="Path for the output HTML file (default: index.html).",
    )
    return parser


parser = _build_parser()


def _cli_main() -> None:
    """Internal CLI entry point to avoid module-level side effects on import."""
    args = parser.parse_args()

    input_path = Path(args.quotes_input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")

    main(quotes_input=input_path, output_html=args.output_html)


if __name__ == "__main__":
    _cli_main()
