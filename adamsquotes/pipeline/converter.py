"""
Pipeline stage 1 (alternate): new-format raw quotes → tagged markdown.

Migrated from ``processNewQuotes.py``.  Uses ``format_tagged_quote`` from
:mod:`adamsquotes.text_utils` for the output format, and all the structural
heuristics from that module.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Tuple

from adamsquotes.text_utils import (
    _clean_text,
    _contains_url,
    _is_dash_line,
    _is_italic_marker,
    _is_title_like,
    _is_url,
    _ends_with_sentence_punct,
    _unwrap_paragraphs,
    format_tagged_quote,
)


def _looks_like_attribution(line: str) -> bool:
    """Return True if the line structurally looks like a source/author/link.

    Uses ONLY structural heuristics — no hardcoded book/author names.
    """
    L = line.strip()
    if not L:
        return False

    if _is_url(L):
        return True

    if L.lower().startswith("from:") and len(L) > 6:
        return True

    if "excerpt from" in L.lower():
        return True

    if _is_italic_marker(L):
        return True

    if _is_title_like(L):
        return True

    if re.match(r"^[-–—]\s*\w", L):
        return True

    if re.match(r"^usr\s+\w+\s+in\s+https?://", L):
        return True

    if L.startswith("-") and len(L) < 80:
        return True

    if " on " in L.lower() and len(L) < 80:
        parts = L.lower().split(" on ", 1)
        if len(parts[0]) < 30 and parts[0].strip():
            return True

    if re.search(r"https?://\S+$", L):
        return True

    if len(L) <= 100 and not _ends_with_sentence_punct(L):
        signals = 0
        if "," in L:
            signals += 1
        if re.search(r"\d{4}", L):
            signals += 1
        if re.search(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,}", L):
            signals += 1
        if L.startswith("*") or L.endswith("*"):
            signals += 1
        if re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$", L):
            signals += 1
        if signals >= 1:
            return True

    return False


def _parse_attribution_line(combined_text: str) -> Dict[str, str]:
    """Parse combined attribution text into source/author/link using only structure."""
    result: Dict[str, str] = {"source": "", "author": "", "link": ""}
    clean = combined_text.strip()

    url = _contains_url(clean)
    if url:
        result["link"] = url
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

    clean = clean.strip("-–—*").strip()

    on_match = re.match(r"^(.+?)\s+on\s+(.+)$", clean)
    if on_match:
        result["author"] = on_match.group(1).strip()
        result["source"] = clean
        return result

    usr_match = re.match(r"^usr\s+(\w+)\s+in\s+(.+)$", clean)
    if usr_match:
        result["author"] = usr_match.group(1)
        result["source"] = clean
        return result

    if "," not in clean:
        name_pattern = r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$"
        if re.match(name_pattern, clean):
            result["author"] = clean
            return result
        handle_pattern = r"^[a-zA-Z0-9_\-]+$"
        if re.match(handle_pattern, clean) and len(clean) > 2:
            result["author"] = clean
            return result
        result["source"] = clean
        return result

    parts = [p.strip() for p in clean.split(",", 1)]
    p0, p1 = parts[0], parts[1]

    if p0.startswith(("The ", "A ", "An ")):
        result["source"] = p0
        result["author"] = p1
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
        result["author"] = p0
        result["source"] = p1
    elif re.match(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}$", p1):
        result["source"] = p0
        result["author"] = p1
    else:
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

    if "this material may be protected by copyright" in lines[-1].strip().lower():
        lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()
    if not lines:
        return [], attribution

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

    peeled: List[str] = []
    for i in range(len(lines) - 1, -1, -1):
        L = lines[i].strip()
        if not L:
            if peeled:
                continue
            continue
        if _looks_like_attribution(L):
            peeled.insert(0, L)
            if len(peeled) >= 3:
                break
        elif peeled:
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
    """Format a single quote as tagged output, with cleaning and unwrapping."""
    return format_tagged_quote(quote_text, source, author, link, note, clean=True)


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
