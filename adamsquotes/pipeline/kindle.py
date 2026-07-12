"""Import Kindle highlight JSON exports into tagged Markdown."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any


KINDLE_TAGS = ("#sciencefiction", "#technology")


class KindleImportError(ValueError):
    """Raised when a Kindle export does not have the expected structure."""


@dataclass(frozen=True)
class KindleHighlight:
    """A validated, normalized Kindle highlight."""

    text: str
    source: str
    author: str
    link: str
    note: str
    tags: str = " ".join(KINDLE_TAGS)


@dataclass(frozen=True)
class KindleBook:
    """Validated metadata and quote-bearing highlights from one export."""

    title: str
    authors: str
    highlights: tuple[KindleHighlight, ...]
    skipped: int


@dataclass(frozen=True)
class ImportResult:
    """Counts reported after a successful import."""

    written: int
    skipped: int
    replaced: int


def _required_string(data: dict[str, Any], field: str, context: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise KindleImportError(f"{context} field '{field}' must be a non-empty string")
    return value


def parse_kindle_data(
    data: Any, tags: Sequence[str] = KINDLE_TAGS
) -> KindleBook:
    """Validate Kindle export data and return normalized highlight records."""
    if not isinstance(data, dict):
        raise KindleImportError("Kindle export must be a JSON object")

    title = _required_string(data, "title", "Top-level")
    authors = _required_string(data, "authors", "Top-level")
    raw_highlights = data.get("highlights")
    if not isinstance(raw_highlights, list):
        raise KindleImportError("Top-level field 'highlights' must be a list")

    highlight_tags = " ".join(tags)
    highlights: list[KindleHighlight] = []
    skipped = 0
    for index, raw in enumerate(raw_highlights):
        context = f"Highlight {index + 1}"
        if not isinstance(raw, dict):
            raise KindleImportError(f"{context} must be an object")
        is_note_only = raw.get("isNoteOnly")
        if not isinstance(is_note_only, bool):
            raise KindleImportError(f"{context} field 'isNoteOnly' must be a boolean")
        if is_note_only:
            skipped += 1
            continue

        text = _required_string(raw, "text", context)
        location = raw.get("location")
        if not isinstance(location, dict):
            raise KindleImportError(f"{context} field 'location' must be an object")
        link = _required_string(location, "url", f"{context} location")
        note = raw.get("note")
        if note is not None and not isinstance(note, str):
            raise KindleImportError(f"{context} field 'note' must be a string or null")
        highlights.append(
            KindleHighlight(text, title, authors, link, note or "", highlight_tags)
        )

    return KindleBook(title, authors, tuple(highlights), skipped)


def parse_kindle_json(
    text: str, tags: Sequence[str] = KINDLE_TAGS
) -> KindleBook:
    """Decode and validate a Kindle JSON document."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KindleImportError(f"Invalid JSON: {exc.msg}") from exc
    return parse_kindle_data(data, tags)


def serialize_highlights(highlights: tuple[KindleHighlight, ...]) -> str:
    """Serialize normalized highlights using tagged Markdown conventions."""
    blocks = []
    for highlight in highlights:
        blocks.append(
            "\n".join(
                (
                    f"*quote:*\t{highlight.text}",
                    f"*source:*\t{highlight.source}",
                    f"*author:*\t{highlight.author}",
                    f"*link:*\t{highlight.link}",
                    f"*note:*\t{highlight.note}",
                    f"*tags:*\t{highlight.tags}",
                )
            )
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


_BLOCK_START = re.compile(r"(?m)^\*quote:\*")


def _field(block: str, name: str, next_name: str) -> str | None:
    match = re.search(
        rf"(?ms)^\*{name}:\*[ \t]*(.*?)\n\*{next_name}:\*", block
    )
    return match.group(1).strip() if match else None


def replace_book_records(
    existing: str, markdown: str, title: str, authors: str
) -> tuple[str, int]:
    """Replace matching source/author blocks while preserving unrelated text."""
    starts = list(_BLOCK_START.finditer(existing))
    if not starts:
        prefix = existing
        retained: list[str] = []
    else:
        prefix = existing[: starts[0].start()]
        retained = []

    replaced = 0
    for index, start in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(existing)
        block = existing[start.start() : end]
        if _field(block, "source", "author") == title and _field(
            block, "author", "link"
        ) == authors:
            replaced += 1
        else:
            retained.append(block)

    result = prefix + "".join(retained)
    if markdown:
        if result and not result.endswith("\n\n"):
            result = result.rstrip("\n") + "\n\n"
        result += markdown
    return result, replaced


def process_kindle_file(
    input_path: str | Path,
    output_path: str | Path,
    processed_output: str | Path,
    tags: Sequence[str] = KINDLE_TAGS,
) -> ImportResult:
    """Validate an export, then write its standalone and aggregate Markdown."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    processed_output = Path(processed_output)

    book = parse_kindle_json(input_path.read_text(encoding="utf-8"), tags)
    markdown = serialize_highlights(book.highlights)
    existing = (
        processed_output.read_text(encoding="utf-8")
        if processed_output.exists()
        else ""
    )
    aggregate, replaced = replace_book_records(
        existing, markdown, book.title, book.authors
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed_output.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    processed_output.write_text(aggregate, encoding="utf-8")
    return ImportResult(len(book.highlights), book.skipped, replaced)
