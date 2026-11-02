"""Batch-import Kindle exports and re-render the site.

Used by the ``Ingest Kindle highlights`` GitHub Actions workflow, which runs it
on JSON files uploaded to ``data/kindle/`` in a pull request.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
import re

from adamsquotes.pipeline.html_renderer import parse_quotes, write_html
from adamsquotes.pipeline.kindle import (
    book_markdown_path,
    parse_kindle_json,
    process_kindle_file,
)
from adamsquotes.types import (
    DEFAULT_HEADER,
    DEFAULT_HTML_OUTPUT,
    DEFAULT_PROCESSED_INPUT,
)

# A hashtag needs at least one letter, so issue references like "#22" are ignored.
_HASHTAG = re.compile(r"(?<![\w#])#(?=\w*[^\W\d_])\w+", flags=re.UNICODE)


@dataclass(frozen=True)
class IngestedBook:
    """Summary of one imported export."""

    export: Path
    title: str
    authors: str
    markdown: Path
    written: int
    skipped: int
    replaced: int


def extract_hashtags(text: str) -> tuple[str, ...]:
    """Return unique hashtags from free text (e.g. a PR title), in order."""
    seen: dict[str, None] = {}
    for tag in _HASHTAG.findall(text):
        seen.setdefault(tag, None)
    return tuple(seen)


def ingest_exports(
    exports: Sequence[str | Path],
    tags: Sequence[str],
    markdown_dir: str | Path = "markdown_quotes",
    processed_output: str | Path = DEFAULT_PROCESSED_INPUT,
) -> list[IngestedBook]:
    """Import each export into its per-book file and the aggregate file.

    Every export is validated before anything is written, so one malformed
    upload does not leave a half-imported batch.
    """
    books = []
    for export in map(Path, exports):
        book = parse_kindle_json(export.read_text(encoding="utf-8"), tags)
        books.append((export, book, book_markdown_path(book.title, markdown_dir)))

    results = []
    for export, book, markdown in books:
        result = process_kindle_file(export, markdown, processed_output, tags)
        results.append(
            IngestedBook(
                export,
                book.title,
                book.authors,
                markdown,
                result.written,
                result.skipped,
                result.replaced,
            )
        )
    return results


def render_site(
    processed_input: str | Path = DEFAULT_PROCESSED_INPUT,
    output_html: str | Path = DEFAULT_HTML_OUTPUT,
    header: str | Path = DEFAULT_HEADER,
) -> int:
    """Render the aggregate Markdown to HTML and return the quote count."""
    quotes = parse_quotes(Path(processed_input).read_text(encoding="utf-8"))
    write_html(quotes, output_path=output_html, header_path=header)
    return len(quotes)


def summary_markdown(books: Sequence[IngestedBook], tags: Sequence[str]) -> str:
    """Build a Markdown report suitable for a PR comment."""
    tag_text = " ".join(f"`{t}`" for t in tags) if tags else "_none (title/author tags only)_"
    lines = [
        "### Kindle import",
        "",
        f"Tags from PR title: {tag_text}",
        "",
        "| Book | Author | Imported | Note-only skipped | Replaced |",
        "|---|---|---:|---:|---:|",
    ]
    for b in books:
        lines.append(
            f"| {b.title} | {b.authors} | {b.written} | {b.skipped} | {b.replaced} |"
        )
    return "\n".join(lines) + "\n"
