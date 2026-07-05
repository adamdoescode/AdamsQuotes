# Adam's collection of random quotes from whatever I've been reading

A simple project to pretty print my quotes collection to an HTML page.

## Quick start

This project uses [uv](https://docs.astral.sh/uv/) for Python package and project management.

```sh
# Install dependencies (pandas)
uv sync

# Process the sample quotes into index.html
uv run python processQuotes.py

# Or specify custom input/output files
uv run python processQuotes.py \
    --quotes_input markdown_quotes/sampleQuotesProcessed.md \
    --output-html my-quotes.html
```

All dependencies are defined in `pyproject.toml` and are installed automatically by `uv sync`.

## How to process quotes

Quotes initially come in unprocessed, e.g in `markdown_quotes/sampleQuotesUnprocessed.md`. We process these using `addTagsToRawQuotes.py` which outputs to `markdown_quotes/sampleQuotesSemiProcessed.md` by default and then these can be manually curated before "publishing" by running them as input to `processQuotes.py` which outputs to `index.html` by default.

## Viewing index.html

The user exposed part of the website is `index.html` which is styled by `style.css` and has some table of contents handling in `index.js`.

## CLI reference for addTagsToRawQuotes.py

```
usage: addTagsToRawQuotes.py [-h] [-o OUTPUT] [input]

Add tags to raw quotes to produce a semi-processed markdown file.

positional arguments:
  input                Path to the raw quotes markdown file (default:
                       markdown_quotes/sampleQuotesUnprocessed.md).

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Path for the output semi-processed markdown file
                       (default: markdown_quotes/sampleQuotesSemiProcessed.md).
```

## CLI reference for processQuotes.py

```
usage: processQuotes.py [-h] [--quotes_input QUOTES_INPUT] [--output-html OUTPUT_HTML]

Process a markdown quotes file into an HTML file.

options:
  -h, --help            show this help message and exit
  --quotes_input QUOTES_INPUT
                        Path to the input markdown file (must have .md suffix).
                        (default: markdown_quotes/sampleQuotesProcessed.md)
  --output-html OUTPUT_HTML
                        Path for the output HTML file.
                        (default: index.html)
```

## Input format

The input markdown file must use the following tags to structure each quote:

```
*quote:*
The content of the quote, which can span
multiple lines if needed.
*source:*
The book, article, or other source where the quote came from
*author:*
The person who said or wrote the quote
*link:*
A URL for further reference (optional)
*note:*
A personal note or commentary about the quote,
which can also span multiple lines.
```

An example of a fully processed input file is `markdown_quotes/sampleQuotesProcessed.md`.



## Output

The script generates a standalone HTML page with:
- A **table of contents** listing every quote title linked to its section on the page.
- Each quote rendered in its own `<div class="quote">` with unique `id`, plus classes for the quote text, source, author, link, and any notes.
- The HTML scaffold is provided by `Header.html` — edit that file to customise the page header/footer and styling.

## Workflow

1. **Add tags** — `addTagsToRawQuotes.py` semi-automatically inserts `*quote:*`, `*source:*`, etc. into raw quote text.
2. **Curate** — Manually fix any tagging errors in the output.
3. **Process** — Run `processQuotes.py` to convert the curated markdown into a styled HTML page.

## Adding in quotes from a different source

`markdown_quotes/new_quotes_unprocessed.md` includes quotes taken from an old [quotes.md](./Sync/menagerie/ideas/quotes.md) file buried in my "ideas" folder (i.e. old notes folder).

Yesterday, I got Deepseek v4 flash to build `processNewQuotes.py` which does a reasonable job converting the contents of `new_quotes_unprocessed.md` to a usable format in `new_quotes_tagged.md`. The script now also:
- [x] remaps spurious escape characters (e.g. `\'`, `\"`, `\--`, `\-`) back to their intended characters.
- [x] unwraps hard-wrapped paragraphs so each paragraph appears on a single line, preserving blank-line breaks between paragraphs.

## Original notes (December 2022)

First, I took my quotes as raw text and did some minor formatting to add spaces etc.

I then attempted to add some identifying tags (e.g "quote" and "source) to each quote in a semi-automated fashion.

To do this I wrote the script `addTagsToRawQuotes.py` which takes the raw quotes text and adds the tags.

In the spirit of efficiency over writing more code, I then manually curated the output so that it actually made sense. The result of this was `markdown_quotes/sampleQuotesProcessed.md` which is included in this repo.

I then fed this curated markdown text into the `processQuotes.py` file which generates a bunch of html divs with the quotes nicely formatted. It then injects this into the `Header.html` file which contains a simple header for the final page (`index.html`).
