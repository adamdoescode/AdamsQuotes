"""
Data model for quotes.

Replaces the handwritten ``Quote`` class from ``processQuotes.py`` with a
clean ``dataclass``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib


@dataclass
class Quote:
    """A single quote with its metadata, ready for HTML rendering.

    Attributes:
        quote: The quote text itself (always present).
        source: The book, article, or person the quote is attributed to.
        note: A personal note or commentary about the quote.
        link: A URL for further reference (optional).
        author: The person who said or wrote the quote (optional).
        tags: Semantic hashtags for searching and browsing.
        id_for_quote: HTML anchor; ``assign_stable_ids`` derives it from content.
        title: A shortened version of the quote, used in the table of contents.
    """

    quote: str = ""
    source: str = ""
    note: str = ""
    link: str = ""
    author: str = ""
    tags: list[str] = field(default_factory=list)
    id_for_quote: str = ""
    title: str = ""

    def generate_title(self) -> None:
        """Derive a short title from the quote text for the table of contents.

        Rules:
            - If the quote is empty, the title is empty.
            - If the quote has 8 words or fewer, the title is the full quote.
            - Otherwise the title is the first 8 words followed by an ellipsis.
        """
        words = self.quote.split()
        if len(words) == 0:
            self.title = ""
        elif len(words) <= 8:
            self.title = self.quote
        else:
            self.title = " ".join(words[:8]) + "..."

    def content_id(self) -> str:
        """Return an anchor ID derived from the quote text, source and author."""
        key = "\x1f".join((self.quote, self.source, self.author))
        return "q" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


def assign_stable_ids(quotes: list[Quote]) -> None:
    """Give each quote a deterministic, page-unique anchor ID.

    IDs depend only on quote content, so re-rendering unchanged input produces
    identical HTML. Exact duplicate quotes get ``-2``, ``-3``... suffixes in
    document order.
    """
    seen: dict[str, int] = {}
    for quote in quotes:
        base = quote.content_id()
        seen[base] = seen.get(base, 0) + 1
        quote.id_for_quote = base if seen[base] == 1 else f"{base}-{seen[base]}"
