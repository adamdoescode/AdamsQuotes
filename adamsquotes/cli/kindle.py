"""CLI entry point for importing Kindle highlight JSON."""

from __future__ import annotations

import argparse
from pathlib import Path

from adamsquotes.pipeline.kindle import KindleImportError, parse_kindle_json, process_kindle_file


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import Kindle highlights into tagged Markdown."
    )
    parser.add_argument("input", help="Path to a Kindle highlights JSON export.")
    parser.add_argument(
        "-o", "--output", help="Per-book Markdown output (default: derived from title)."
    )
    parser.add_argument(
        "--processed-output",
        default="markdown_quotes/QuotesProcessed.md",
        help="Aggregate Markdown output (default: markdown_quotes/QuotesProcessed.md).",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    input_path = Path(args.input)
    processed_output = Path(args.processed_output)
    if input_path.suffix.lower() != ".json":
        parser.error("Input file must have a .json suffix")
    if processed_output.suffix.lower() != ".md":
        parser.error("Processed output file must have a .md suffix")

    output_path: Path
    if args.output:
        output_path = Path(args.output)
    else:
        try:
            book = parse_kindle_json(input_path.read_text(encoding="utf-8"))
        except (OSError, KindleImportError) as exc:
            parser.error(str(exc))
        if Path(book.title).name != book.title:
            parser.error("Book title cannot contain path separators")
        output_path = Path("markdown_quotes") / f"{book.title}.md"
    if output_path.suffix.lower() != ".md":
        parser.error("Output file must have a .md suffix")

    try:
        result = process_kindle_file(input_path, output_path, processed_output)
    except (OSError, KindleImportError) as exc:
        parser.error(str(exc))
    print(
        f"Written: {result.written}; skipped: {result.skipped}; "
        f"replaced: {result.replaced}"
    )


if __name__ == "__main__":
    main()
