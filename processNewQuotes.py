"""
Process new_quotes_unprocessed.md format into tagged output for processQuotes.py.

The new-format markdown uses:
  - Title line
  - Dash separator line (mostly dashes/hyphens)
  - Quote body (multi-paragraph, may be long)
  - Attribution line(s) at the end (source, author, link)

Output is meant for manual curation before feeding into processQuotes.py.

Usage::

    uv run python processNewQuotes.py
    uv run python processNewQuotes.py path/to/input.md -o path/to/output.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ── Helpers ─────────────────────────────────────────────────────────────────


def _is_dash_line(line: str) -> bool:
    """Return True if a line is mostly (80%+) dashes/hyphens."""
    stripped = line.strip()
    if len(stripped) < 3:
        return False
    dash_count = (
        stripped.count("-") + stripped.count("\u2014") + stripped.count("\u2013")
    )
    return dash_count / max(len(stripped), 1) >= 0.8


def _is_url(text: str) -> bool:
    text = text.strip().strip("<>")
    return bool(re.match(r"^https?://\S+$", text))


def _contains_url(text: str) -> Optional[str]:
    m = re.search(r"(https?://\S+)", text)
    if m:
        return m.group(1).rstrip(">")
    return None


def _is_italic_marker(text: str) -> bool:
    """Lines wrapped in *asterisks* — common markdown for book titles."""
    t = text.strip()
    return t.startswith("*") and t.endswith("*") and len(t) > 4


def _ends_with_sentence_punct(text: str) -> bool:
    """True if the text ends with sentence-ending punctuation (. ! ?)."""
    t = text.strip()
    if not t:
        return False
    # URLs ending in slashes or brackets don't count
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


def _looks_like_attribution(line: str) -> bool:
    """Return True if the line structurally looks like a source/author/link.

    Uses ONLY structural heuristics — no hardcoded book/author names.
    """
    L = line.strip()
    if not L:
        return False

    # URL-only lines are always attribution
    if _is_url(L):
        return True

    # "From: http://..." style
    if L.lower().startswith("from:") and len(L) > 6:
        return True

    # "Excerpt from" always attribution
    if "excerpt from" in L.lower():
        return True

    # Italic-marked lines (*Book Title*) are attribution
    if _is_italic_marker(L):
        return True

    # Lines starting with dash/emdash prefix
    if re.match(r"^[-–—]\s*\w", L):
        return True

    # "usr ixtl in https://" pattern
    if re.match(r"^usr\s+\w+\s+in\s+https?://", L):
        return True

    # "-eeyore_ on reddit" pattern
    if L.startswith("-") and len(L) < 80:
        return True

    # "username on website" pattern: short line (< 80), short first part
    if " on " in L.lower() and len(L) < 80:
        parts = L.lower().split(" on ", 1)
        if len(parts[0]) < 30 and parts[0].strip():
            return True

    # Lines ending with a URL (no space after http)
    if re.search(r"https?://\S+$", L):
        return True

    # Attribution lines are typically short and DON'T end with sentence punctuation
    # But we need at least ONE additional structual signal to avoid eating quote text
    if len(L) <= 100 and not _ends_with_sentence_punct(L):
        signals = 0
        if "," in L:
            signals += 1
        if re.search(r"\d{4}", L):  # year numbers
            signals += 1
        if re.search(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,}", L):  # 3+ capitalized words
            signals += 1
        if L.startswith("*") or L.endswith("*"):
            signals += 1
        # Single line of 2-3 capitalized words (name pattern, e.g. "Aldous Huxley")
        if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$", L):
            signals += 1
        if signals >= 1:
            return True

    return False


def _parse_attribution_line(combined_text: str) -> Dict[str, str]:
    """Parse combined attribution text into source/author/link using only structure."""
    result: Dict[str, str] = {"source": "", "author": "", "link": ""}
    clean = combined_text.strip()

    # Extract URLs first
    url = _contains_url(clean)
    if url:
        result["link"] = url
        # Remove URL from the text to parse remaining
        clean = (
            clean
            .replace(url, "")
            .replace("<>", "")
            .strip()
            .strip(",")
            .strip("-")
            .strip(":")
            .strip()
        )
        if not clean:
            return result

    # Strip structural markers
    clean = clean.strip("-–—*").strip()

    # "X on Y" pattern → X is author, Y as source
    on_match = re.match(r"^(.+?)\s+on\s+(.+)$", clean)
    if on_match:
        result["author"] = on_match.group(1).strip()
        result["source"] = clean
        return result

    # "usr X in Y" → X is author, Y is context
    usr_match = re.match(r"^usr\s+(\w+)\s+in\s+(.+)$", clean)
    if usr_match:
        result["author"] = usr_match.group(1)
        result["source"] = clean
        return result

    # Single word/name with no comma → likely a bare author name (e.g. "Richard Feynman")
    if "," not in clean:
        # Check if it looks like a person's name (2-3 capitalized words)
        name_pattern = r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$"
        if re.match(name_pattern, clean):
            result["author"] = clean
            return result
        # Check for common online handles
        handle_pattern = r"^[a-zA-Z0-9_\-]+$"
        if re.match(handle_pattern, clean) and len(clean) > 2:
            result["author"] = clean
            return result
        # Everything else short → source
        result["source"] = clean
        return result

    # Comma-separated: try to split book vs author structurally
    parts = [p.strip() for p in clean.split(",", 1)]
    p0, p1 = parts[0], parts[1]

    # Heuristics for which order: "Book, Author" vs "Author, Book"
    # If first part starts with article → likely book
    if p0.startswith(("The ", "A ", "An ")):
        result["source"] = p0
        result["author"] = p1
    # If first looks like a name (2-3 words, capitalized) and second looks like a name too
    # Could be either. Check if second contains words typical of book titles
    elif p1.startswith((
        "The ",
        "A ",
        "An ",
        "Voyage",
        "Against",
        "Hackers",
        "But You",
        "Lies",
        "History",
        "Rise",
    )):
        result["author"] = p0
        result["source"] = p1
    elif re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$", p0):
        # p0 looks like a name → Author, Book
        result["author"] = p0
        result["source"] = p1
    elif re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$", p1):
        # p1 looks like a name → Book, Author
        result["source"] = p0
        result["author"] = p1
    else:
        # Can't tell — put everything in source
        result["source"] = clean

    return result


def _parse_excerpt_from(lines: List[str]) -> Dict[str, str]:
    """Parse an ``Excerpt from`` multi-line attribution block."""
    result: Dict[str, str] = {"source": "", "author": "", "link": ""}
    for i, line in enumerate(lines):
        if "excerpt from" in line.lower():
            for j in range(i + 1, len(lines)):
                if lines[j].strip():
                    result["source"] = lines[j].strip().strip("*")
                    for k in range(j + 1, len(lines)):
                        if lines[k].strip():
                            ac = lines[k].strip().strip("*")
                            if (
                                "copyright" not in ac.lower()
                                and "protected" not in ac.lower()
                            ):
                                result["author"] = ac
                            break
                    break
            break
    for line in lines:
        url = _contains_url(line)
        if url:
            result["link"] = url
            break
    return result


def _find_attribution(body_lines: List[str]) -> Tuple[List[str], List[str]]:
    """Split body_lines into (quote_lines, attribution_lines).

    Uses purely structural heuristics — no hardcoded names.
    """
    lines = list(body_lines)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return [], []

    attribution: List[str] = []

    # Strip copyright protection notices
    if "this material may be protected by copyright" in lines[-1].strip().lower():
        lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()
    if not lines:
        return [], attribution

    # Detect "Excerpt from" blocks (scan from end)
    excerpt_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if "excerpt from" in lines[i].strip().lower():
            excerpt_idx = i
            break
    if excerpt_idx is not None:
        attribution = lines[excerpt_idx:]
        quote_lines = lines[:excerpt_idx]
        while quote_lines and not quote_lines[-1].strip():
            quote_lines.pop()
        return quote_lines, attribution

    # Peel trailing attribution lines using structural heuristics
    # Allow up to 3 trailing lines to be attribution
    peeled: List[str] = []
    for i in range(len(lines) - 1, -1, -1):
        L = lines[i].strip()
        if not L:
            if peeled:
                continue  # skip blank lines between attribution lines
            continue
        if _looks_like_attribution(L):
            peeled.insert(0, L)
            if len(peeled) >= 3:
                break
        elif peeled:
            # We had started peeling but hit a non-attribution line — stop
            break
        else:
            break

    if peeled:
        attribution = peeled
        quote_lines = lines[: -len(peeled)]
        while quote_lines and not quote_lines[-1].strip():
            quote_lines.pop()
        return quote_lines, attribution

    return lines, []


def split_blocks(text: str) -> List[Dict[str, str]]:
    """Split raw text into quote blocks using index-based iteration."""
    lines = text.splitlines()

    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "Quote list:":
            start = i + 2
            break

    content = lines[start:]
    blocks: List[Dict[str, str]] = []
    i = 0
    n = len(content)

    while i < n:
        line = content[i].strip()
        if not line:
            i += 1
            continue

        # Title line is followed by a dash line
        if i + 1 < n and _is_dash_line(content[i + 1]):
            title = line
            i += 2
            body_lines: List[str] = []
            while i < n:
                cl = content[i].strip()
                if cl and i + 1 < n and _is_dash_line(content[i + 1]):
                    break
                body_lines.append(content[i])
                i += 1
            blocks.append({"title": title, "body": "\n".join(body_lines).strip()})
        else:
            i += 1

    return blocks


def _build_quote_output(
    quote_text: str,
    source: str = "",
    author: str = "",
    link: str = "",
    note: str = "",
) -> str:
    return (
        f"*quote:*\t{quote_text}\n"
        f"*source:*\t{source}\n"
        f"*author:*\t{author}\n"
        f"*link:*\t{link}\n"
        f"*note:*\t{note}\n"
    )


def process_file(input_path: Path, output_path: Path) -> None:
    """Read, process, and write the tagged output."""
    text = input_path.read_text(encoding="utf-8")
    blocks = split_blocks(text)

    output_parts: List[str] = []
    stats = {"total": 0, "with_source": 0, "with_author": 0, "with_link": 0}
    errors: List[str] = []

    for block in blocks:
        title = block["title"]
        body = block["body"]
        if not body:
            errors.append(title)
            continue

        body_lines = body.splitlines()
        quote_lines, attribution_lines = _find_attribution(body_lines)
        quote_text = "\n".join(quote_lines).strip() if quote_lines else body.strip()
        if not quote_text:
            errors.append(title)
            continue

        source = author = link = ""
        if attribution_lines:
            if any("excerpt from" in l.lower() for l in attribution_lines):
                info = _parse_excerpt_from(attribution_lines)
            else:
                combined = " ".join(
                    l.strip().strip("-–—*").strip()
                    for l in attribution_lines
                    if l.strip()
                )
                info = _parse_attribution_line(combined)
            source = info.get("source", "")
            author = info.get("author", "")
            link = info.get("link", "")

        if not link:
            url_in_quote = _contains_url(quote_text)
            if url_in_quote:
                link = url_in_quote

        stats["total"] += 1
        if source:
            stats["with_source"] += 1
        if author:
            stats["with_author"] += 1
        if link:
            stats["with_link"] += 1

        output_parts.append(_build_quote_output(quote_text, source, author, link))

    result = "\n".join(output_parts)
    output_path.write_text(result, encoding="utf-8")

    print(f"✓ Processed {stats['total']} quotes -> {output_path}")
    print(
        f"  {stats['with_source']} with source  |  {stats['with_author']} with author  |  {stats['with_link']} with link"
    )
    if errors:
        print(f"  {len(errors)} quote(s) with empty body")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Process new_quotes_unprocessed.md format into tagged output.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=str,
        default="markdown_quotes/new_quotes_unprocessed.md",
        help="Path to the raw quotes markdown file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="markdown_quotes/new_quotes_tagged.md",
        help="Path for the output tagged markdown file.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    input_path = Path(args.input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")
    process_file(input_path, Path(args.output))


if __name__ == "__main__":
    main()
