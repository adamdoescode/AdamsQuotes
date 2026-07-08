"""
Shared constants and type definitions for the adamsquotes package.

Tag schema, known authors list, and default file paths used across the
pipeline stages.
"""

from typing import Final, List

# ── Tag schema constants ─────────────────────────────────────────────────────

QUOTE_TAG: Final[str] = "*quote:*"
SOURCE_TAG: Final[str] = "*source:*"
AUTHOR_TAG: Final[str] = "*author:*"
LINK_TAG: Final[str] = "*link:*"
NOTE_TAG: Final[str] = "*note:*"

ALL_TAGS: Final[List[str]] = [
    QUOTE_TAG,
    SOURCE_TAG,
    AUTHOR_TAG,
    LINK_TAG,
    NOTE_TAG,
]

# ── Known authors (case-insensitive, titlecased on output) ──────────────────

KNOWN_AUTHORS: List[str] = [
    "tim low",
    "david foster wallace",
    "steve silberman",
    "jennifer doudna",
    "mark twain",
    "charles darwin",
    "alastair reynolds",
    "adam rutherford",
    "david quammen",
    "sam harris",
]

# ── Default file paths ──────────────────────────────────────────────────────

DEFAULT_RAW_INPUT: Final[str] = "markdown_quotes/sampleQuotesUnprocessed.md"
DEFAULT_SEMI_OUTPUT: Final[str] = "markdown_quotes/sampleQuotesSemiProcessed.md"
DEFAULT_NEW_INPUT: Final[str] = "markdown_quotes/new_quotes_unprocessed.md"
DEFAULT_NEW_OUTPUT: Final[str] = "markdown_quotes/new_quotes_tagged.md"
DEFAULT_PROCESSED_INPUT: Final[str] = "markdown_quotes/QuotesProcessed.md"
DEFAULT_HTML_OUTPUT: Final[str] = "index.html"
DEFAULT_HEADER: Final[str] = "Header.html"
