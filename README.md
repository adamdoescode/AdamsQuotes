# Adam's collection of random quotes from whatever I've been reading

[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/downloads/)
[![GitHub Pages](https://github.com/adamdoescode/AdamsQuotes/actions/workflows/pages/pages-build-deployment/badge.svg?branch=main)](https://github.com/adamdoescode/AdamsQuotes/actions/workflows/pages/pages-build-deployment)

A simple project to pretty print my quotes collection to an HTML page.

## Quick start

This project uses [uv](https://docs.astral.sh/uv/) for Python package and project management.

```sh
# Install dependencies
uv sync

# Process the sample quotes into index.html
uv run adamsquotes-render

# Or specify custom input/output files
uv run adamsquotes-render \
    --quotes_input markdown_quotes/sampleQuotesProcessed.md \
    --output-html my-quotes.html
```

All dependencies are defined in `pyproject.toml` and are installed automatically by `uv sync`.

## Pipeline stages

| Stage | CLI command | What it does |
|---|---|---|
| 1. Tag | `uv run adamsquotes-tag` | Raw quotes → semi-processed tagged markdown |
| 1 (alt). Convert | `uv run adamsquotes-convert` | New-format raw quotes → tagged markdown |
| 1 (alt). Kindle import | `uv run adamsquotes-kindle <export.json>` | Kindle JSON → tagged per-book and aggregate markdown |
| 1.5. LLM Clean | `uv run adamsquotes-clean` | LLM cleanup of tagged markdown |
| 2. Render | `uv run adamsquotes-render` | Tagged markdown → styled HTML page |

You can also run each stage via its module directly:

```sh
uv run python -m adamsquotes.cli.tagger
uv run python -m adamsquotes.cli.converter
uv run python -m adamsquotes.cli.llm_cleaner
uv run python -m adamsquotes.cli.renderer
uv run python -m adamsquotes.cli.kindle data/kindle/Kindle.Highlights_Accelerando_1783512733914.json
```

## Importing Kindle highlights

Import the supplied Accelerando export with:

```sh
uv run adamsquotes-kindle data/kindle/Kindle.Highlights_Accelerando_1783512733914.json
```

Set the tags applied to every imported highlight with `--tags`:

```sh
uv run adamsquotes-kindle data/kindle/Kindle.Highlights_Accelerando_1783512733914.json \
    --tags '#sciencefiction' '#technology' '#novel'
```

By default this writes `markdown_quotes/Accelerando.md` and adds the records to
`markdown_quotes/QuotesProcessed.md`. Use `-o/--output` to choose the per-book
file, `--processed-output` to choose the aggregate file, and `--tags TAG
[TAG ...]` to replace the default tag list. Inputs must end in `.json`, and
both outputs must end in `.md`.

The importer maps highlight `text` to `*quote:*`, the export title and authors
to `*source:*` and `*author:*`, `location.url` to `*link:*`, and `note` to
`*note:*` (with null notes left empty). Every imported highlight receives
`#sciencefiction #technology` by default. Note-only entries are skipped.
Rerunning an import replaces aggregate records with the exact same source and
author, so it does not create duplicates or disturb other books.

## How to process quotes

Quotes initially come in unprocessed, e.g in `markdown_quotes/sampleQuotesUnprocessed.md`. We process these using `uv run adamsquotes-tag` which outputs to `markdown_quotes/sampleQuotesSemiProcessed.md` by default and then these can be manually curated before "publishing" by running them as input to `uv run adamsquotes-render` which outputs to `index.html` by default.

## Viewing index.html

The user exposed part of the website is `index.html` which is styled by `style.css` and has some table of contents handling in `index.js`.

## Validating GitHub Pages

GitHub Pages runs this repository through Jekyll before publishing. Use Ruby
3.3, matching `.ruby-version` and CI. The local validation command uses the
same pinned `github-pages` gem stack as CI:

```sh
bundle install
make validate
```

The Jekyll config excludes quote source files and project source directories
from the published site. The intended published files are the root static
assets: `index.html`, `style.css`, and `index.js`.

`make validate` runs both checks used by CI:

```sh
bundle exec jekyll build --safe --trace
uv run pytest
```

## CLI reference for adamsquotes-tag

```
usage: adamsquotes-tag [-h] [-o OUTPUT] [input]

Add tags to raw quotes to produce a semi-processed markdown file.

positional arguments:
  input                Path to the raw quotes markdown file (default:
                       markdown_quotes/sampleQuotesUnprocessed.md).

options:
  -h, --help           show this help message and exit
  -o, --output OUTPUT  Path for the output semi-processed markdown file
                       (default: markdown_quotes/sampleQuotesSemiProcessed.md).
```

## CLI reference for adamsquotes-render

```
usage: adamsquotes-render [-h] [--quotes_input QUOTES_INPUT] [--output-html OUTPUT_HTML]

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
*tags:*
Exactly two curated semantic hashtags, separated by a space.
```

An example of a fully processed input file is `markdown_quotes/sampleQuotesProcessed.md`.

Legacy files without `*tags:*` still render; those quotes simply have no tag chips.

### Manual semantic tagging

When asking ChatGPT to add semantic tags to a processed quote file, use these rules:
- Read each quote and preserve all existing quote, source, author, link, and note text exactly.
- Add one `*tags:*` field after each `*note:*` field.
- Supply exactly two space-separated hashtags per quote.
- Use semantic tags describing topics, themes, domains, or use cases, not generic labels like `#quote`.



## Output

The script generates a standalone HTML page with:
- A **table of contents** listing every quote title linked to its section on the page.
- Each quote rendered in its own `<div class="quote">` with unique `id`, plus classes for the quote text, source, author, link, any notes, and semantic tag chips.
- A static search box that filters quote cards by visible quote text, metadata, notes, or hashtags.
- A collapsible hashtag browser listing every unique hashtag and its quote count; selecting one applies the same shareable `?tag=` filter used by quote tag chips.
- The HTML scaffold is provided by `Header.html` — edit that file to customise the page header/footer and styling.

## Workflow

1. **Add tags** — `uv run adamsquotes-tag` inserts `*quote:*`, `*source:*`, etc. into raw quote text.
2. **Curate** — Manually fix any tagging errors in the output.
3. **Process** — Run `uv run adamsquotes-render` to convert the curated markdown into a styled HTML page.

## Adding in quotes from a different source

`markdown_quotes/new_quotes_unprocessed.md` includes quotes taken from an old [quotes.md](./Sync/menagerie/ideas/quotes.md) file buried in my "ideas" folder (i.e. old notes folder).

The `adamsquotes-convert` command does a reasonable job converting the contents of `new_quotes_unprocessed.md` to a usable format in `new_quotes_tagged.md`. It also:
- [x] remaps spurious escape characters (e.g. `\'`, `\"`, `\--`, `\-`) back to their intended characters.
- [x] unwraps hard-wrapped paragraphs so each paragraph appears on a single line, preserving blank-line breaks between paragraphs.
- [x] detects short, title-like attribution lines (e.g. `Voyage of the Beagle`, `Against the Gods`, `Australians vol 1`) using structural heuristics rather than hardcoded names.
- [x] treats sentence-ending punctuation inside closing quotation marks (e.g. `purposes.") as a sentence ending, so quote text isn't accidentally peeled into the attribution.

### Claude...

There's some further issues but I think they are bespoke enough that I should just shove the whole thing into free claude. I gave it this prompt:
>This markdown file contains quotes that have been partially standardised into a simple plaintext format. However there are several inconsistencies such as the attribution (source) being clipped or one quote being split across two entries. Manually read through the entire file and then write a new file `new_quotes_claude_processed.md` with the identified errors corrected. Do not write a script to process these.

We'll see if that works! If I hit the context limit we'll look into feeding the markdown to Deepseek in async chunks for parsing. Certainly a pile of short requests should be *fast* if expensive (probably on the order of a few cents total).

Welp, yeah it crashed out on me. That's when I built `adamsquotes-clean` (or equivalently `scripts/processTaggedQuotesWithLLM.py`) which calls deepseek via OpenRouter API to process the quotes in chunks.

## Original notes (December 2022, updated July 2026)

First, I took my quotes as raw text and did some minor formatting to add spaces etc.

I then attempted to add some identifying tags (e.g "quote" and "source) to each quote in a semi-automated fashion using the first tagger scripts.

After manual curation I used the renderer to generate a styled HTML page.

The project has since been refactored into the structured ``adamsquotes`` package with a clean CLI interface — see the pipeline stages above for the modern workflow.
