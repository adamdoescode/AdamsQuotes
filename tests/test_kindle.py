"""Tests for the Kindle JSON import pipeline."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adamsquotes.cli.kindle import _build_parser
from adamsquotes.pipeline.kindle import (
    KindleImportError,
    parse_kindle_data,
    parse_kindle_json,
    process_kindle_file,
    replace_book_records,
    serialize_highlights,
)


def kindle_data() -> dict[str, object]:
    return {
        "title": "Accelerando",
        "authors": "Charles Stross",
        "highlights": [
            {
                "text": "First — with Unicode ‘punctuation’.",
                "isNoteOnly": False,
                "location": {"url": "kindle://first", "value": 1},
                "note": None,
            },
            {
                "text": "Second quote.",
                "isNoteOnly": False,
                "location": {"url": "kindle://second", "value": 2},
                "note": "Useful annotation",
            },
            {"text": "not a passage", "isNoteOnly": True, "note": "A note"},
        ],
    }


def test_parse_and_serialize_preserves_order_and_fields() -> None:
    book = parse_kindle_data(kindle_data())

    assert [highlight.text for highlight in book.highlights] == [
        "First — with Unicode ‘punctuation’.",
        "Second quote.",
    ]
    assert book.skipped == 1
    assert serialize_highlights(book.highlights) == (
        "*quote:*\tFirst — with Unicode ‘punctuation’.\n"
        "*source:*\tAccelerando\n*author:*\tCharles Stross\n"
        "*link:*\tkindle://first\n*note:*\t\n"
        "*tags:*\t#sciencefiction #technology\n\n"
        "*quote:*\tSecond quote.\n*source:*\tAccelerando\n"
        "*author:*\tCharles Stross\n*link:*\tkindle://second\n"
        "*note:*\tUseful annotation\n*tags:*\t#sciencefiction #technology\n"
    )


def test_custom_tags_are_applied_to_every_highlight() -> None:
    book = parse_kindle_data(kindle_data(), ["#fiction", "#space-opera"])

    assert {highlight.tags for highlight in book.highlights} == {
        "#fiction #space-opera"
    }


def test_cli_accepts_tag_list() -> None:
    args = _build_parser().parse_args(
        ["input.json", "--tags", "#fiction", "#space-opera"]
    )

    assert args.tags == ["#fiction", "#space-opera"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data.pop("title"),
        lambda data: data.update(authors=""),
        lambda data: data.update(highlights={}),
        lambda data: data["highlights"][0].update(text=""),  # type: ignore[index,union-attr]
        lambda data: data["highlights"][0].update(location={}),  # type: ignore[index,union-attr]
        lambda data: data["highlights"][0].update(note=4),  # type: ignore[index,union-attr]
    ],
)
def test_malformed_data_is_rejected(mutate: object) -> None:
    data = kindle_data()
    mutate(data)  # type: ignore[operator]
    with pytest.raises(KindleImportError):
        parse_kindle_data(data)


def test_invalid_json_is_rejected() -> None:
    with pytest.raises(KindleImportError, match="Invalid JSON"):
        parse_kindle_json("{")


def test_process_is_idempotent_and_preserves_other_records(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    standalone = tmp_path / "Accelerando.md"
    aggregate = tmp_path / "QuotesProcessed.md"
    source.write_text(json.dumps(kindle_data()), encoding="utf-8")
    other = (
        "*quote:*\tOther\n*source:*\tAnother book\n*author:*\tSomeone\n"
        "*link:*\t\n*note:*\t\n*tags:*\t#one #two\n"
    )
    aggregate.write_text(other, encoding="utf-8")

    first = process_kindle_file(source, standalone, aggregate)
    second = process_kindle_file(source, standalone, aggregate)

    assert (first.written, first.skipped, first.replaced) == (2, 1, 0)
    assert (second.written, second.skipped, second.replaced) == (2, 1, 2)
    result = aggregate.read_text(encoding="utf-8")
    assert result.count("*source:*\tAccelerando") == 2
    assert other.rstrip() in result


def test_process_uses_custom_tags(tmp_path: Path) -> None:
    source = tmp_path / "input.json"
    standalone = tmp_path / "Accelerando.md"
    aggregate = tmp_path / "QuotesProcessed.md"
    source.write_text(json.dumps(kindle_data()), encoding="utf-8")

    process_kindle_file(source, standalone, aggregate, ["#novel", "#ai"])

    assert standalone.read_text(encoding="utf-8").count(
        "*tags:*\t#novel #ai"
    ) == 2


def test_validation_failure_does_not_change_outputs(tmp_path: Path) -> None:
    source = tmp_path / "bad.json"
    standalone = tmp_path / "book.md"
    aggregate = tmp_path / "all.md"
    source.write_text('{"title": "book"}', encoding="utf-8")
    standalone.write_text("standalone", encoding="utf-8")
    aggregate.write_text("aggregate", encoding="utf-8")

    with pytest.raises(KindleImportError):
        process_kindle_file(source, standalone, aggregate)

    assert standalone.read_text(encoding="utf-8") == "standalone"
    assert aggregate.read_text(encoding="utf-8") == "aggregate"


def test_replacement_requires_exact_source_and_author() -> None:
    existing = (
        "*quote:*\tKeep\n*source:*\tAccelerando\n*author:*\tAnother author\n"
        "*link:*\t\n*note:*\t\n*tags:*\t#one #two\n"
    )
    result, replaced = replace_book_records(
        existing, "", "Accelerando", "Charles Stross"
    )
    assert result == existing
    assert replaced == 0
