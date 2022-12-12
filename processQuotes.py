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

with open("sampleQuotesProcessed.md", "r") as quotesFile:
    quotes = quotesFile.read()

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
        #these will be used for div class names - i dont think this gets used?? TODO
        self.tags = {
            '*quote*': 'quote',
            '*source:*': 'source',
            '*note:*': 'note',
            '*link:*': 'link',
            '*author:*': 'author',
        }
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
        for RawQuote in self.linesFromFile.split('*Quote*')[1:]:
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
            newQuote.quote = RawQuote.split('*Source:*')[0].strip()
            newQuote.source = RawQuote.split('*Source:*')[1].split('*Author:*')[0].strip()
            newQuote.author = RawQuote.split('*Author:*')[1].split('*Link:*')[0].strip()
            newQuote.link = RawQuote.split('*Link:*')[1].split('*Note:*')[0].strip()
            newQuote.note = RawQuote.split('*Note:*')[1].strip()
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
        with open('index.html', 'w') as quotesFile:
            for quote in self.QuotesList:
                quotesFile.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="style.css">
    <title>Document</title>
</head>''')
                quotesFile.write(f'<div class="quote" id="{quote.id}">\n')
                if quote.note != '':
                    quotesFile.write(f'  <p class="note">{quote.note}</p>\n')
                quotesFile.write(f'  <p class="quote-text">{quote.quote}</p>\n')
                if quote.source != '':
                    quotesFile.write(f'  <p class="source">{quote.source}</p>\n')
                quotesFile.write('</div>\n')
                quotesFile.write('</body>\n</html>')

processedQuotes = ProcessQuotes(quotes).processQuotes()
processedQuotes.printQuotes(2)
#processedQuotes.writeQuotes()
# %%
processedQuotes.QuotesList
# %%
