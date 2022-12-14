#%%
'''
A script to process quotes from a markdown text file into a html file.

First a script is used to pre-process the markdown file to have tags for easier parsing.
Then I manually curated the pre-processed markdown to fix up broken quotes.

This script then processes that file into a readable format, 
generates a html file with divs for each quote. Includes classes and IDs for css styles.

TODO Each quote will be contained within a div with a class of "quote".
TODO div elements will be boxes (TODO flexbox) with a border and padding.
TODO Each quote will have a class of "quote" and a unique id.
'''

#random int
from random import randint
from typing import List, Dict

#%%

class Quote:
    '''
    A class to hold simple quote information
    Does not include HTML features!
    '''
    def __init__(self):
        self.quote: str = '' #always present
        self.source: str = ''
        self.note: str = ''
        self.link: str = '' #sometimes present
        self.author: str = '' #sometimes present
        '''
        Very simple random generator for now, 
        maybe replace with something more meaningful if that turns out to be useful
        Maybe for alternating div colours.
        '''
        self.id = randint(10000,99999)

class ProcessQuotes:
    '''
    Processes quotes from markdown file into html divs.
    '''
    def __init__(self, quotes: str):
        self.linesFromFile = quotes #raw quotes List with string items
        #a list to hold our quotes in as a Quote class
        self.QuotesList: List[Quote] = []

    def processQuotes(self):
        '''
        Coordinating function that cycles through quote lines
        First we split by the quote tag so that:
            1. the quote is the first line
            2. the source and note are within the same block of text
            (but on seperate lines somewhere)
        '''
        for RawQuote in self.linesFromFile.split('*quote:*')[1:]:
            '''
            Order is always the same, so we can just split by tag:
            1. quote (possibly multiline)
            2. source
            3. author
            4. link
            5. note (possibly multiline)
            '''
            # linesIterator = iter(RawQuote.splitlines())
            newQuote = Quote()
            newQuote.quote = RawQuote.split('*source:*')[0].strip()
            newQuote.source = RawQuote.split('*source:*')[1].split('*author:*')[0].strip()
            newQuote.author = RawQuote.split('*author:*')[1].split('*link:*')[0].strip()
            newQuote.link = RawQuote.split('*link:*')[1].split('*note:*')[0].strip()
            newQuote.note = RawQuote.split('*note:*')[1].strip()
            self.QuotesList.append(newQuote)
        return self

    def printQuotes(self, numQuotes: int = None):
        counter = 0
        for quote in self.QuotesList:
            if counter == numQuotes:
                break
            print(f'quote: {quote.quote}')
            print(f'source: {quote.source}')
            print(f'note: {quote.note}')
            print(f'id: {quote.id}')
            print()
            counter += 1

    def writeQuotes(self):
        # get headerAndFooter scaffold
        with open('Header.html', 'r') as headerAndFooterFile:
            headerAndFooter = headerAndFooterFile.read()
        #now we generate a string of the quotes with divs etc
        quotesHtmlFormatted = ''
        for quote in self.QuotesList:
            quotesHtmlFormatted += f'<div class="quote" id="{quote.id}">\n'
            if quote.note != '':
                #iterate through each paragraph and pass as <p> tag
                for note in quote.note.splitlines():
                    quotesHtmlFormatted += f'  <p class="note">{note}</p>\n'
            #do the same for the potentatially multiline quote
            for quoteLine in quote.quote.splitlines():
                quotesHtmlFormatted += f'  <p class="quote-text">{quoteLine}</p>\n'
            #source
            if quote.source != '':
                quotesHtmlFormatted += f'  <p class="source"><span class="source-source">Source:</span> {quote.source}</p>\n'
            #author
            if quote.author != '':
                quotesHtmlFormatted += f'  <p class="author"><span class="tag-author">Author:</span> {quote.author}</p>\n'
            #link
            if quote.link != '':
                quotesHtmlFormatted += f'  <p class="link"><span class="tag-link">Link:</span> <a class="tag-link-href" href="{quote.link}">{quote.link}<a></p>\n'
            quotesHtmlFormatted += '</div>\n'
        headerAndFooter = headerAndFooter.replace('<!--quotes-->', quotesHtmlFormatted)
        with open('index.html', 'w') as quotesFile:
            quotesFile.write(headerAndFooter)

with open("sampleQuotesProcessed.md", "r") as quotesFile:
    quotes = quotesFile.read()

processedQuotes = ProcessQuotes(quotes).processQuotes()
processedQuotes.printQuotes(2)
processedQuotes.writeQuotes()
# %%
