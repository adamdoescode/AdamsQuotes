"""
Shared text-processing utilities used by multiple pipeline stages.

Consolidates logic previously duplicated across ``addTagsToRawQuotes.py``,
``processNewQuotes.py``, and ``processQuotes.py``:

- URL detection (``_is_url``, ``_contains_url``)
- Text cleaning (``_clean_text``, ``_unwrap_paragraphs``)
- Structural heuristics (``_is_dash_line``, ``_is_italic_marker``,
  ``_is_title_like``, ``_ends_with_sentence_punct``)
"""

from __future__ import annotations

import re
from typing import Optional


def _normalise_authors() -> dict:
    """Return a dict mapping lowercase author names to titlecase versions."""
    # Local import to avoid circular dependency at package level
    from adamsquotes.types import KNOWN_AUTHORS

    return {a.lower(): a.title() for a in KNOWN_AUTHORS}


def _detect_author(text: str, author_map: dict) -> str:
    """Return the titlecased author name if found in *text*, else empty string."""
    for lower_name, title_name in author_map.items():
        if lower_name in text.lower():
            return title_name
    return ""


# ── URL helpers ──────────────────────────────────────────────────────────────


def _is_url(text: str) -> bool:
    """Return True if *text* is a bare URL (optionally wrapped in ``<>``)."""
    t = text.strip().strip("<>")
    return bool(re.match(r"^https?://\S+$", t))


def _contains_url(text: str) -> Optional[str]:
    """Return the first URL found in *text*, or ``None``."""
    m = re.search(r"(https?://\S+)", text)
    if m:
        return m.group(1).rstrip(">")
    return None


# ── Text cleaning ────────────────────────────────────────────────────────────


def _clean_text(text: str) -> str:
    """Remove spurious backslash escapes from *text*."""
    escape_remap = {
        r"\'": "'",
        r"\"": '"',
        r"\--": "--",
        r"\-": "-",
        r"\#": "#",
        r"\. . .": "...",
        r"\.\.\.": "...",
    }
    for old, new in escape_remap.items():
        text = text.replace(old, new)
    return text


def _unwrap_paragraphs(text: str) -> str:
    """Join hard-wrapped lines into single paragraphs, preserving blank-line breaks."""
    paragraphs = text.split("\n\n")
    unwrapped: list[str] = []
    for paragraph in paragraphs:
        lines = [line.strip() for line in paragraph.splitlines()]
        if any(line.startswith((">", "-", "*", "#")) for line in lines if line):
            unwrapped.append(paragraph)
        else:
            joined = " ".join(line for line in lines if line)
            unwrapped.append(joined)
    return "\n\n".join(unwrapped)


# ── Structural heuristics ────────────────────────────────────────────────────


def _is_dash_line(line: str) -> bool:
    """Return True if a line is mostly (80%+) dashes/hyphens."""
    stripped = line.strip()
    if len(stripped) < 3:
        return False
    dash_count = (
        stripped.count("-") + stripped.count("\u2014") + stripped.count("\u2013")
    )
    return dash_count / max(len(stripped), 1) >= 0.8


def _is_italic_marker(text: str) -> bool:
    """Lines wrapped in ``*asterisks*`` — common markdown for book titles."""
    t = text.strip()
    return t.startswith("*") and t.endswith("*") and len(t) > 4


def _is_title_like(text: str) -> bool:
    """True if *text* structurally looks like a book/article title."""
    t = text.strip()
    if not t or len(t) > 60:
        return False
    if _ends_with_sentence_punct(t):
        return False

    small_words = {
        "the", "a", "an", "of", "and", "or", "but",
        "in", "on", "at", "to", "for", "with", "by",
        "from", "vol", "ca", "bc", "ce",
    }
    words = t.split()
    if not words:
        return False

    meaningful = 0
    has_capitalized = False
    for w in words:
        if w[0].isupper():
            has_capitalized = True
            meaningful += 1
        elif w.lower() in small_words or w.isdigit():
            meaningful += 1

    return has_capitalized and meaningful / len(words) >= 0.5


def _ends_with_sentence_punct(text: str) -> bool:
    """True if *text* ends with sentence-ending punctuation (. ! ?)."""
    t = text.strip()
    if not t:
        return False
    # Strip a trailing quote mark so "purposes." is detected as ending.
    t = t.rstrip('"').rstrip("'")
    if t.endswith((".", "!", "?")):
        # Common abbreviations that end with periods
        abbrev_pattern = (
            r"(?:vol|ed|pp?|ca|vs|et\s+al|dept|St|No|Dr|Mr|Ms|Mrs|fig|ch|sec)\.$"
        )
        if re.search(abbrev_pattern, t, re.IGNORECASE):
            return False
        # Numeric suffixes like "1929-1941." or "vol 1."
        if re.search(r"(?:19|20)\d{2}\.-\d{4}\.?$", t):
            return False
        if re.search(r"\d+\.$", t):
            return False
        return True
    return False


def format_tagged_quote(
    quote: str,
    source: str = "",
    author: str = "",
    link: str = "",
    note: str = "",
    clean: bool = True,
) -> str:
    """Format a single quote into the tagged output string, optionally cleaning.

    Args:
        quote: The quote text.
        source: The source of the quote.
        author: The author of the quote.
        link: A URL for further reference.
        note: A personal note or commentary.
        clean: Whether to apply ``_clean_text`` / ``_unwrap_paragraphs``.

    Returns:
        A tagged string with ``*quote:*``, ``*source:*``, etc.
    """
    if clean:
        quote, source, author, link, note = map(
            _clean_text, (quote, source, author, link, note)
        )
        quote = _unwrap_paragraphs(quote)
    return (
        f"*quote:*\t{quote}\n"
        f"*source:*\t{source}\n"
        f"*author:*\t{author}\n"
        f"*link:*\t{link}\n"
        f"*note:*\t{note}\n"
    )