"""Process tagged markdown quotes into a styled HTML page.

This script is the second stage of a three-stage pipeline:
  1. `addTagsToRawQuotes.py`  — semi-automatically inserts ``*quote:*``,
     ``*source:*``, and other tags into raw quote text.
  2. *Manual curation*       — fixing broken tags in the output from stage 1.
  3. This script             — parses the curated markdown and generates a
     complete HTML page with a table of contents, styled quote divs, and
     unique element IDs.

Typical usage::

    uv run python processQuotes.py
    uv run python processQuotes.py --quotes_input my_quotes.md --output-html out.html
"""

from random import randint
from pathlib import Path
from typing import List, Dict
import argparse
import pandas as pd


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

    def __init__(self):
        self.quote: str = ""  # always present
        self.source: str = ""
        self.note: str = ""
        self.link: str = ""  # sometimes present
        self.author: str = ""  # sometimes present
        # Random 5-digit ID used as the HTML anchor for this quote.
        self.idForQuote = randint(10000, 99999)
        self.title: str = ""

    def generateTitle(self) -> "Quote":
        """Derive a short title from the quote text for the table of contents.

        Rules:
            - If the quote is empty, the title is empty.
            - If the quote has 8 words or fewer, the title is the full quote.
            - Otherwise the title is the first 8 words followed by an ellipsis.

        Returns:
            Self, with ``self.title`` populated.
        """
        # split the quote into a list of words
        quoteWords = self.quote.split()
        # if the quote is less than 8 words, use the whole quote
        # deal with empty quotes too
        if len(quoteWords) == 0:
            self.title = ""
        # if the quote is 8 or fewer words, use the whole quote
        elif len(quoteWords) <= 8:
            self.title = self.quote
        # if the quote is more than 8 words, use the first 8 words and add an ellipsis
        elif len(quoteWords) > 8:
            self.title = " ".join(quoteWords[:8]) + "..."
        return self


class ProcessQuotes:
    """Parse tagged markdown quotes and produce an HTML page of styled quotes.

    The input is expected to be a markdown string with tags such as
    ``*quote:*``, ``*source:*``, ``*author:*``, ``*link:*``, and ``*note:*``
    delimiting each quote's fields.

    Attributes:
        lines_from_file: The raw markdown text.
        quotes_list: List of parsed ``Quote`` objects.
        quote_titles: Mapping from quote title to its numeric HTML anchor ID.
    """

    def __init__(self, quotes: str):
        self.linesFromFile: str = quotes
        self.QuotesList: List[Quote] = []
        self.QuoteTitles: Dict[str, int] = {}

    def createQuoteTitles(self, quote: Quote) -> "ProcessQuotes":
        """Register a quote's title and ID in the table-of-contents mapping.

        Args:
            quote: A ``Quote`` whose ``title`` and ``idForQuote`` are stored.

        Returns:
            Self, for method chaining.
        """
        self.QuoteTitles[quote.title] = quote.idForQuote
        return self

    def addClassToTD(self, table: str) -> str:
        """Add numbered CSS classes to ``<td>`` elements in an HTML table.

        This allows the *source* column to be hidden via CSS on narrow
        viewports (responsive design).

        Args:
            table: An HTML table string.

        Returns:
            The same table with ``class="column0"``, ``class="column1"``, etc.
            added to each ``<td>``, and matching ``class`` attributes on
            ``<th>`` elements.
        """
        # first we fix up the th elements
        table = table.replace("<th>title</th>", '<th class="column0">title</th>')
        table = table.replace("<th>source</th>", '<th class="column1">source</th>')
        # split the table by line
        lines = table.splitlines()
        columnCounter = 0
        # iterate through the lines
        for index, line in enumerate(lines):
            if "<tr>" in line:
                columnCounter = 0
            # look for td elements
            if "<td>" in line:
                # add class with column number
                lines[index] = line.replace(
                    "<td>", f'<td class="column{columnCounter}">'
                )
                columnCounter += 1
            # debug print
            if columnCounter > 2:
                print(f"columnCounter > 2, currently at {columnCounter}")
        # rejoin the lines into a table
        return "\n".join(lines)

    def writeTableOfContents(self) -> str:
        """Build an HTML table-of-contents linking to each quote's anchor.

        Uses pandas to render a two-column table (*title* and *source*)
        where each title is a hyperlink to the corresponding quote's
        ``<div>`` on the same page.

        Returns:
            An HTML ``<div class="table-of-contents">`` block.
        """
        # start the table of contents
        tableOfContents = '<div class="table-of-contents">\n'
        tableOfContentsDictForPandas = {column: [] for column in ["title", "source"]}
        # itertate through the quotes in the QuoteTitles dict
        for quote in self.QuotesList:
            # add the index, title, and blank columns to the table of contents dict
            titleLink = f'  <a class="tableOfContents" href="#{quote.idForQuote}">{quote.title}</a>'
            tableOfContentsDictForPandas["title"].append(titleLink)
            # truncate source length in title
            if len(quote.source) > 30:
                tableOfContentsDictForPandas["source"].append(quote.source[:30] + "...")
            else:
                tableOfContentsDictForPandas["source"].append(quote.source)
        tableOfContents += pd.DataFrame(tableOfContentsDictForPandas).to_html(
            header=True, justify="left", border=0, render_links=True, index=False
        )
        # need to fix a unicode translation issue
        tableOfContents = tableOfContents.replace("&lt;", "<").replace("&gt;", ">")
        # add classes to the table of contents
        tableOfContents = self.addClassToTD(tableOfContents)
        # make sure to include a closing div tag
        return tableOfContents + "</div>\n"

    def processQuotes(self) -> "ProcessQuotes":
        """Parse the raw markdown into ``Quote`` objects.

        Splits the input text on ``*quote:*`` tags and extracts each field
        in order:

            1. quote (possibly multi-line)
            2. source
            3. author
            4. link
            5. note (possibly multi-line)

        Returns:
            Self with ``quotes_list`` and ``quote_titles`` populated.
        """
        for RawQuote in self.linesFromFile.split("*quote:*")[1:]:
            # Order is always the same, so we can just split by tag:
            # 1. quote (possibly multiline)
            # 2. source
            # 3. author
            # 4. link
            # 5. note (possibly multiline)
            newQuote = Quote()
            newQuote.quote = RawQuote.split("*source:*")[0].strip()
            newQuote.source = (
                RawQuote.split("*source:*")[1].split("*author:*")[0].strip()
            )
            newQuote.author = RawQuote.split("*author:*")[1].split("*link:*")[0].strip()
            newQuote.link = RawQuote.split("*link:*")[1].split("*note:*")[0].strip()
            newQuote.note = RawQuote.split("*note:*")[1].strip()
            # generate a title for the quote
            newQuote.generateTitle()
            # then we add the quote to the QuoteTitles dict for use in a table of contents
            self.createQuoteTitles(newQuote)
            self.QuotesList.append(newQuote)
        return self

    def printQuotes(self, numQuotes: int | None = None) -> None:
        """Print a summary of parsed quotes to stdout (useful for debugging).

        Args:
            numQuotes: Maximum number of quotes to print, or ``None`` for all.
        """
        counter = 0
        for quote in self.QuotesList:
            if numQuotes is not None and counter >= numQuotes:
                break
            print(f"quote: {quote.quote}")
            print(f"source: {quote.source}")
            print(f"note: {quote.note}")
            print(f"id: {quote.idForQuote}")
            print()
            counter += 1

    def writeQuoteAttributeToFile(self, quote: Quote) -> str:
        """Render a single ``Quote`` as an HTML ``<div>`` block.

        The output includes optional sections for title, note, quote text,
        source, author, and link — each wrapped in a ``<p>`` with a
        descriptive CSS class.

        Args:
            quote: The ``Quote`` object to render.

        Returns:
            An HTML string for one quote ``<div>``.
        """
        quoteInHTML = ""
        quoteInHTML += f'<div class="quote" id="{quote.idForQuote}">\n'
        if quote.title != "":
            quoteInHTML += f'  <p class="quote-title">{quote.title}</p>\n'
        if quote.note != "":
            # iterate through each paragraph and pass as <p> tag
            for note in quote.note.splitlines():
                quoteInHTML += f'  <p class="note">{note}</p>\n'
        # do the same for the potentatially multiline quote
        for quoteLine in quote.quote.splitlines():
            quoteInHTML += f'  <p class="quote-text">{quoteLine}</p>\n'
        # source
        if quote.source != "":
            quoteInHTML += f'  <p class="source"><span class="source-source">Source:</span> {quote.source}</p>\n'
        # author
        if quote.author != "":
            quoteInHTML += f'  <p class="author"><span class="tag-author">Author:</span> {quote.author}</p>\n'
        # link
        if quote.link != "":
            quoteInHTML += f'  <p class="link"><span class="tag-link">Link:</span> <a class="tag-link-href" href="{quote.link}">{quote.link}<a></p>\n'
        quoteInHTML += "</div>\n"
        return quoteInHTML

    def generateHtml(self, header_template: str) -> str:
        """
        Generates the full HTML page as a string by injecting the table of contents
        and quotes into the header template.

        Args:
            header_template: The HTML header/footer scaffold string.

        Returns:
            The complete HTML page as a string.
        """
        result = header_template.replace(
            "<!-- table of contents -->", self.writeTableOfContents()
        )
        quotes_html = ""
        for quote in self.QuotesList:
            quotes_html += self.writeQuoteAttributeToFile(quote)
        result = result.replace("<!--quotes-->", quotes_html)
        return result

    def writeQuotes(self, output_path: str | Path = "index.html") -> None:
        """Render all parsed quotes to an HTML file.

        Loads the header/footer scaffold from ``Header.html``, generates the
        full page via :meth:`generateHtml`, and writes the result to disk.

        Args:
            output_path: Destination path for the output HTML file.
        """
        # get headerAndFooter scaffold
        with open("Header.html", "r") as headerAndFooterFile:
            headerAndFooter = headerAndFooterFile.read()
        html = self.generateHtml(header_template=headerAndFooter)
        with open(output_path, "w") as quotesFile:
            quotesFile.write(html)


def main(quotes_input: str | Path, output_html: str | Path = "index.html") -> None:
    """
    Process a markdown file of quotes and write the result to an HTML file.

    Args:
        quotes_input: Path to the input markdown file (must have .md suffix).
        output_html: Path for the output HTML file (defaults to 'index.html').
    """
    quotes_path = Path(quotes_input)
    output_path = Path(output_html)

    with quotes_path.open("r") as quotesFile:
        quotes = quotesFile.read()
    processedQuotes = ProcessQuotes(quotes).processQuotes()
    processedQuotes.writeQuotes(output_path)


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Process a markdown quotes file into an HTML file."
    )
    parser.add_argument(
        "--quotes_input",
        type=str,
        default="sampleQuotesProcessed.md",
        help="Path to the input markdown file (must have .md suffix).",
    )
    parser.add_argument(
        "--output-html",
        type=str,
        default="index.html",
        help="Path for the output HTML file (default: index.html).",
    )
    return parser


parser = _build_parser()


if __name__ == "__main__":
    args = parser.parse_args()

    input_path = Path(args.quotes_input)
    if input_path.suffix != ".md":
        parser.error(f"Input file must have a .md suffix, got '{input_path.suffix}'")

    main(quotes_input=input_path, output_html=args.output_html)
