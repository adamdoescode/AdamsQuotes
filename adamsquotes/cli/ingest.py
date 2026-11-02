"""CLI entry point: import Kindle exports, then re-render ``index.html``."""

from __future__ import annotations

import argparse
from pathlib import Path

from adamsquotes.pipeline.ingest import (
    extract_hashtags,
    ingest_exports,
    render_site,
    summary_markdown,
)
from adamsquotes.pipeline.kindle import KindleImportError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import Kindle highlight exports and re-render the site."
    )
    parser.add_argument("exports", nargs="+", help="Kindle highlights JSON exports.")
    parser.add_argument(
        "--tags",
        nargs="*",
        default=[],
        metavar="TAG",
        help="Tags added to every highlight.",
    )
    parser.add_argument(
        "--tags-from-text",
        default="",
        metavar="TEXT",
        help="Also take #hashtags from this text (e.g. a PR title).",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        help="Write a Markdown import report to this path.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)
    exports = [Path(p) for p in args.exports]
    for export in exports:
        if export.suffix.lower() != ".json":
            parser.error(f"Export must have a .json suffix: {export}")

    tags = tuple(dict.fromkeys((*args.tags, *extract_hashtags(args.tags_from_text))))
    try:
        books = ingest_exports(exports, tags)
    except (OSError, KindleImportError) as exc:
        parser.error(str(exc))
    count = render_site()

    report = summary_markdown(books, tags)
    if args.summary:
        args.summary.write_text(report, encoding="utf-8")
    print(report)
    print(f"Rendered {count} quotes.")


if __name__ == "__main__":
    main()
