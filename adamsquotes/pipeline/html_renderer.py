"""
Standalone functions for rendering tagged quotes into a styled HTML page.

Replaces the ``ProcessQuotes`` class from ``processQuotes.py`` with pure
module-level functions.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from adamsquotes.models import Quote


def parse_quotes(text: str) -> List[Quote]:
    """Parse tagged markdown text into a list of ``Quote`` objects.

    Splits the input on ``*quote:*`` tags and extracts each field in order:

        1. quote (possibly multi-line)
        2. source
        3. author
        4. link
        5. note (possibly multi-line)
        6. tags (optional, space-separated hashtags)

    Args:
        text: The raw tagged markdown text.

    Returns:
        A list of ``Quote`` objects with titles generated.
    """
    quotes: List[Quote] = []
    for raw_quote in text.split("*quote:*")[1:]:
        q = Quote()
        q.quote = raw_quote.split("*source:*", maxsplit=1)[0].strip()
        after_source = raw_quote.split("*source:*", maxsplit=1)[1]
        q.source = after_source.split("*author:*", maxsplit=1)[0].strip()
        after_author = after_source.split("*author:*", maxsplit=1)[1]
        q.author = after_author.split("*link:*", maxsplit=1)[0].strip()
        after_link = after_author.split("*link:*", maxsplit=1)[1]
        q.link = after_link.split("*note:*", maxsplit=1)[0].strip()
        after_note = after_link.split("*note:*", maxsplit=1)[1]
        if "*tags:*" in after_note:
            note, tags = after_note.split("*tags:*", maxsplit=1)
            q.note = note.strip()
            q.tags = tags.strip().split()
        else:
            q.note = after_note.strip()
        q.generate_title()
        quotes.append(q)
    return quotes


def _add_column_classes(table: str) -> str:
    """Add numbered CSS classes to ``<td>`` and ``<th>`` elements."""
    table = table.replace("<th>title</th>", '<th class="column0">title</th>')
    table = table.replace("<th>source</th>", '<th class="column1">source</th>')
    lines = table.splitlines()
    column_counter = 0
    for index, line in enumerate(lines):
        if "<tr>" in line:
            column_counter = 0
        if "<td>" in line:
            lines[index] = line.replace("<td>", f'<td class="column{column_counter}">')
            column_counter += 1
        if column_counter > 2:
            print(f"columnCounter > 2, currently at {column_counter}")
    return "\n".join(lines)


def render_toc(quotes: List[Quote]) -> str:
    """Build an HTML table-of-contents linking to each quote's anchor.

    Args:
        quotes: The list of ``Quote`` objects.

    Returns:
        An HTML ``<div class="table-of-contents">`` block.
    """
    result = '<div class="table-of-contents">\n'
    toc_dict: dict[str, list[str]] = {"title": [], "source": []}
    for quote in quotes:
        title_link = (
            f'  <a class="tableOfContents" href="#{quote.id_for_quote}">'
            f"{quote.title}</a>"
        )
        toc_dict["title"].append(title_link)
        if len(quote.source) > 30:
            toc_dict["source"].append(quote.source[:30] + "...")
        else:
            toc_dict["source"].append(quote.source)

    # Build a simple HTML table without pandas
    result += "<table>\n"
    result += '<tr><th class="column0">title</th><th class="column1">source</th></tr>\n'
    for title, source in zip(toc_dict["title"], toc_dict["source"]):
        result += f"<tr>\n<td>{title}</td>\n<td>{source}</td>\n</tr>\n"
    result += "</table>\n"
    result = _add_column_classes(result)
    return result + "</div>\n"


def render_quote_html(quote: Quote) -> str:
    """Render a single ``Quote`` as an HTML ``<div>`` block.

    Args:
        quote: The ``Quote`` object to render.

    Returns:
        An HTML string for one quote ``<div>``.
    """
    html = f'<div class="quote" id="{quote.id_for_quote}">\n'
    if quote.title:
        html += f'  <p class="quote-title">{quote.title}</p>\n'
    if quote.note:
        for note in quote.note.splitlines():
            html += f'  <p class="note">{note}</p>\n'
    for quote_line in quote.quote.splitlines():
        html += f'  <p class="quote-text">{quote_line}</p>\n'
    if quote.source:
        html += (
            f'  <p class="source"><span class="source-source">Source:</span>'
            f" {quote.source}</p>\n"
        )
    if quote.author:
        html += (
            f'  <p class="author"><span class="tag-author">Author:</span>'
            f" {quote.author}</p>\n"
        )
    if quote.link:
        html += (
            f'  <p class="link"><span class="tag-link">Link:</span>'
            f' <a class="tag-link-href" href="{quote.link}">{quote.link}<a></p>\n'
        )
    if quote.tags:
        html += '  <div class="quote-tags">\n'
        for tag in quote.tags:
            html += f'    <span class="quote-tag">{tag}</span>\n'
        html += "  </div>\n"
    html += "</div>\n"
    return html


def generate_html(quotes: List[Quote], header_template: str) -> str:
    """Generate the full HTML page by injecting TOC and quotes into the template.

    Args:
        quotes: The list of ``Quote`` objects.
        header_template: The HTML header/footer scaffold string.

    Returns:
        The complete HTML page as a string.
    """
    result = header_template.replace("<!-- table of contents -->", render_toc(quotes))
    quotes_html = "".join(render_quote_html(q) for q in quotes)
    result = result.replace("<!--quotes-->", quotes_html)
    return result


def write_html(
    quotes: List[Quote],
    output_path: str | Path = "index.html",
    header_path: str | Path = "Header.html",
) -> None:
    """Render all quotes to an HTML file using the header/footer scaffold.

    Args:
        quotes: The list of ``Quote`` objects.
        output_path: Destination path for the output HTML file.
        header_path: Path to the header/footer scaffold HTML file.
    """
    header_text = Path(header_path).read_text(encoding="utf-8")
    html = generate_html(quotes, header_template=header_text)
    Path(output_path).write_text(html, encoding="utf-8")
