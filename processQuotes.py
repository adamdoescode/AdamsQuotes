# %%
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

# random int
from random import randint
from typing import List, Dict
import pandas as pd


class Quote:
    '''
    A class to hold simple quote information
    Does not include HTML features!
    '''

    def __init__(self):
        self.quote: str = ''  # always present
        self.source: str = ''
        self.note: str = ''
        self.link: str = ''  # sometimes present
        self.author: str = ''  # sometimes present
        '''
        Very simple random generator for now, 
        maybe replace with something more meaningful if that turns out to be useful
        Maybe for alternating div colours.
        '''
        self.idForQuote = randint(10000, 99999)
        self.title: str = ''

    def generateTitle(self):
        '''
        A function to generate a title for the quote.
        Rules for making the title are:
        1. if the quote is less than 8 words, use the whole quote.
        2. if the quote is more than 8 words, use the first 8 words and add an ellipsis.
        '''
        # split the quote into a list of words
        quoteWords = self.quote.split()
        # if the quote is less than 8 words, use the whole quote
        # deal with empty quotes too
        if len(quoteWords) == 0:
            self.title = ''
        elif len(quoteWords) < 8:
            self.title = self.quote
        # if the quote is more than 8 words, use the first 8 words and add an ellipsis
        elif len(quoteWords) > 8:
            self.title = ' '.join(quoteWords[:8]) + '...'
        return self


class ProcessQuotes:
    '''
    Processes quotes from markdown file into html divs.
    '''

    def __init__(self, quotes: str):
        self.linesFromFile = quotes  # raw quotes List with string items
        # a list to hold our quotes in as a Quote class
        self.QuotesList: List[Quote] = []
        '''
        For a table of contents we need a way to reference divs by title.
        Here we create an empty dictionary of titles and ids from each Quote:
        QuoteTitles = Dict[title:str, id:str] for each Quote
        We use the method createQuoteTitles to fill this
        We call this method in processQuotes
        '''
        self.QuoteTitles: Dict[str, str] = {}

    def createQuoteTitles(self, quote: Quote):
        '''
        A function to create a dictionary of titles and ids from each Quote
        '''
        self.QuoteTitles[quote.title] = quote.idForQuote
        return self

    def addClassToTD(self, table: str):
        '''
        A function to add a class to the td elements in a table.
        This is so we can hide the source column on mobile.
        '''
        #first we fix up the th elements
        table = table.replace('<th>title</th>', '<th class="column0">title</th>')
        table = table.replace('<th>source</th>', '<th class="column1">source</th>')
        #split the table by line
        lines = table.splitlines()
        columnCounter = 0
        # iterate through the lines
        for index, line in enumerate(lines):
            if '<tr>' in line:
                columnCounter = 0
            # look for td elements
            if '<td>' in line:
                #add class with column number
                lines[index] = line.replace('<td>', f'<td class="column{columnCounter}">')
                columnCounter += 1
            #debug print
            if columnCounter > 2:
                print(f'columnCounter > 2, currently at {columnCounter}')
        # rejoin the lines into a table
        return '\n'.join(lines)

    def writeTableOfContents(self):
        '''
        Before we write the quotes to the html file we need to write the table of contents.
        We can leverage pandas to print a table to html for this.
        '''
        # start the table of contents
        tableOfContents = '<div class="table-of-contents">\n'
        tableOfContentsDictForPandas = {column: []
                                        for column in ['title', 'source']}
        # itertate through the quotes in the QuoteTitles dict
        for quote in self.QuotesList:
            # add the index, title, and blank columns to the table of contents dict
            titleLink = f'  <a class="tableOfContents" href="#{quote.idForQuote}">{quote.title}</a>'
            tableOfContentsDictForPandas['title'].append(titleLink)
            # truncate source length in title
            if len(quote.source) > 30:
                tableOfContentsDictForPandas['source'].append(
                    quote.source[:30] + '...')
            else:
                tableOfContentsDictForPandas['source'].append(quote.source)
        tableOfContents += pd.DataFrame(tableOfContentsDictForPandas).to_html(
            header=True, justify='left', border=0, render_links=True, index=False
        )
        # need to fix a unicode translation issue
        tableOfContents = tableOfContents.replace(
            '&lt;', '<').replace('&gt;', '>')
        # add classes to the table of contents
        tableOfContents = self.addClassToTD(tableOfContents)
        # make sure to include a closing div tag
        return tableOfContents + '</div>\n'

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
            newQuote.source = RawQuote.split(
                '*source:*')[1].split('*author:*')[0].strip()
            newQuote.author = RawQuote.split(
                '*author:*')[1].split('*link:*')[0].strip()
            newQuote.link = RawQuote.split(
                '*link:*')[1].split('*note:*')[0].strip()
            newQuote.note = RawQuote.split('*note:*')[1].strip()
            # generate a title for the quote
            newQuote.generateTitle()
            # then we add the quote to the QuoteTitles dict for use in a table of contents
            self.createQuoteTitles(newQuote)
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
            print(f'id: {quote.idForQuote}')
            print()
            counter += 1

    def writeQuoteAttributeToFile(self, quote: Quote):
        '''
        A function to write each quote to the html file string
        This function is called from the writeQuotes function
        To generate a table of contents I need to include a class name unique to each header
        '''
        quoteInHTML = ''
        quoteInHTML += f'<div class="quote" id="{quote.idForQuote}">\n'
        if quote.title != '':
            quoteInHTML += f'  <p class="quote-title">{quote.title}</p>\n'
        if quote.note != '':
            # iterate through each paragraph and pass as <p> tag
            for note in quote.note.splitlines():
                quoteInHTML += f'  <p class="note">{note}</p>\n'
        # do the same for the potentatially multiline quote
        for quoteLine in quote.quote.splitlines():
            quoteInHTML += f'  <p class="quote-text">{quoteLine}</p>\n'
        # source
        if quote.source != '':
            quoteInHTML += f'  <p class="source"><span class="source-source">Source:</span> {quote.source}</p>\n'
        # author
        if quote.author != '':
            quoteInHTML += f'  <p class="author"><span class="tag-author">Author:</span> {quote.author}</p>\n'
        # link
        if quote.link != '':
            quoteInHTML += f'  <p class="link"><span class="tag-link">Link:</span> <a class="tag-link-href" href="{quote.link}">{quote.link}<a></p>\n'
        quoteInHTML += '</div>\n'
        return quoteInHTML

    def writeQuotes(self):
        # get headerAndFooter scaffold
        with open('Header.html', 'r') as headerAndFooterFile:
            headerAndFooter = headerAndFooterFile.read()
        #write table of contents by replacing <!-- table of contents -->
        headerAndFooter = headerAndFooter.replace(
            '<!-- table of contents -->', self.writeTableOfContents())
        #write quotes by replacing <!--quotes-->
        quotesHtmlFormatted = ''
        # now we generate a string of the quotes with divs etc
        for quote in self.QuotesList:
            quotesHtmlFormatted += self.writeQuoteAttributeToFile(quote)
        headerAndFooter = headerAndFooter.replace(
            '<!--quotes-->', quotesHtmlFormatted)
        with open('index.html', 'w') as quotesFile:
            quotesFile.write(headerAndFooter)


if __name__ == "__main__":
    with open("sampleQuotesProcessed.md", "r") as quotesFile:
        quotes = quotesFile.read()
    processedQuotes = ProcessQuotes(quotes).processQuotes()
    processedQuotes.writeQuotes()

# %%
