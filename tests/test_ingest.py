"""Tests for batch Kindle ingestion used by the GitHub Actions workflow."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adamsquotes.cli.ingest import main
from adamsquotes.pipeline.ingest import (
    extract_hashtags,
    ingest_exports,
    render_site,
    summary_markdown,
)
from adamsquotes.pipeline.kindle import KindleImportError
from tests.conftest import SAMPLE_HEADER


def export(path: Path, title: str, authors: str = "Some Author") -> Path:
    path.write_text(
        json.dumps(
            {
                "title": title,
                "authors": authors,
                "highlights": [
                    {
                        "text": f"A line from {title}.",
                        "isNoteOnly": False,
                        "location": {"url": f"kindle://{title}", "value": 1},
                        "note": None,
                    },
                    {"text": "", "isNoteOnly": True, "note": "just a note"},
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Add Foundation #sciencefiction #asimov", ("#sciencefiction", "#asimov")),
        ("#22 ingest #birds", ("#birds",)),
        ("dupes #a1 #a1", ("#a1",)),
        ("no tags here", ()),
        ("email me@x.com #ok", ("#ok",)),
        ("double ##hash", ()),
        ("unicode #café", ("#café",)),
    ],
)
def test_extract_hashtags(text: str, expected: tuple[str, ...]) -> None:
    assert extract_hashtags(text) == expected


def test_ingest_writes_per_book_and_aggregate(tmp_path: Path) -> None:
    a = export(tmp_path / "a.json", "Book A")
    b = export(tmp_path / "b.json", "Book B")
    aggregate = tmp_path / "QuotesProcessed.md"
    aggregate.write_text("*quote:*\tOld\n*source:*\tX\n*author:*\tY\n*link:*\n*note:*\n\n")

    books = ingest_exports([a, b], ["#birds"], tmp_path, aggregate)

    assert [x.title for x in books] == ["Book A", "Book B"]
    assert all(x.written == 1 and x.skipped == 1 for x in books)
    text = aggregate.read_text()
    assert "Old" in text and "A line from Book A." in text and "A line from Book B." in text
    assert "#birds #BookA #SomeAuthor" in (tmp_path / "Book A.md").read_text()


def test_ingest_is_idempotent(tmp_path: Path) -> None:
    a = export(tmp_path / "a.json", "Book A")
    aggregate = tmp_path / "QuotesProcessed.md"
    ingest_exports([a], [], tmp_path, aggregate)
    first = aggregate.read_text()
    books = ingest_exports([a], [], tmp_path, aggregate)
    assert aggregate.read_text() == first
    assert books[0].replaced == 1


def test_bad_export_in_batch_writes_nothing(tmp_path: Path) -> None:
    good = export(tmp_path / "good.json", "Good")
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    aggregate = tmp_path / "QuotesProcessed.md"
    with pytest.raises(KindleImportError):
        ingest_exports([good, bad], [], tmp_path, aggregate)
    assert not aggregate.exists()
    assert not (tmp_path / "Good.md").exists()


def test_render_site_writes_html(tmp_path: Path) -> None:
    a = export(tmp_path / "a.json", "Book A")
    aggregate = tmp_path / "QuotesProcessed.md"
    header = tmp_path / "Header.html"
    header.write_text(SAMPLE_HEADER)
    ingest_exports([a], [], tmp_path, aggregate)
    out = tmp_path / "index.html"
    assert render_site(aggregate, out, header) == 1
    assert "A line from Book A." in out.read_text()


def test_summary_lists_books_and_tags(tmp_path: Path) -> None:
    a = export(tmp_path / "a.json", "Book A")
    books = ingest_exports([a], ["#x"], tmp_path, tmp_path / "agg.md")
    report = summary_markdown(books, ["#x"])
    assert "`#x`" in report and "| Book A | Some Author | 1 | 1 | 0 |" in report
    assert "none" in summary_markdown(books, [])


def test_cli_merges_tags_and_writes_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "markdown_quotes").mkdir()
    (tmp_path / "Header.html").write_text(SAMPLE_HEADER)
    a = export(tmp_path / "a.json", "Book A")
    main([str(a), "--tags", "#one", "--tags-from-text", "Add #one #two", "--summary", "s.md"])
    assert "#one #two #BookA" in (tmp_path / "markdown_quotes" / "Book A.md").read_text()
    assert "Book A" in (tmp_path / "s.md").read_text()
    assert (tmp_path / "index.html").exists()


def test_cli_rejects_non_json(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main([str(tmp_path / "x.txt")])
