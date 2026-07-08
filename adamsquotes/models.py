"""
Data model for quotes.

Replaces the handwritten ``Quote`` class from ``processQuotes.py`` with a
clean ``dataclass``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from random import randint


@dataclass
class Quote:
    """A single quote with its metadata, ready for HTML rendering.

    Attributes:
        quote: The quote text itself (always present).
        source: The book, article, or person the quote is attributed to.
        note: A personal note or commentary about the quote.
        link: A URL for further reference (optional).
        author: The person who said or wrote the quote (optional).
        id_for_quote: A random 5-digit numeric ID used as the HTML anchor.
        title: A shortened version of the quote, used in the table of contents.
    """

    quote: str = ""
    source: str = ""
    note: str = ""
    link: str = ""
    author: str = ""
    id_for_quote: int = field(default_factory=lambda: randint(10000, 99999))
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
