# Adam's collection of random quotes from whatever I've been reading

A simple project to pretty print my quotes collection to a HTML page.

This is just practice for my python and html skills.

# How this works

First, I took my quotes as raw text and did some minor formatting to add spaces etc.

I then attempted to add some identifying tags (e.g "quote" and "source) to each quote in a semi-automated fashion.

To do this I wrote the script `addTagsToRawQuotes.py` which takes the raw quotes text and adds the tags.

In the spirit of efficiency over writing more code, I then manually curated the output so that it actually made sense. The result of this was `sampleQuotesProcessed.md` which is included in this repo.

I then fed this curated markdown text into the `processQuotes.py` file which generates a bunch of html divs with the quotes nicely formatted. It then injects this into the `Header.html` file which contains a simple header for the final page (`index.html`).
