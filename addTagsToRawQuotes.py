'''
I want to somewhat automate the process of adding tags to the raw quotes.
Then I can manually go in and fix them up.

I have a raw quotes file: sampleQuotesUnprocessed.md
'''
#%%
from typing import List,Dict
#%%

with open("sampleQuotesUnprocessed.md", "r") as quotesFile:
    quotes = quotesFile.read()

'''
For the sake of speed, we assume that the order of lines within each quote is:
1. quote
2. source
3. note

We can also identify links by the presence of 'http' in the line.

Otherwise we leave things untouched.
'''

knownAuthors: List[str] = [
    'tim low',
    'david foster wallace',
    'steve silberman',
    'jennifer doudna',
    'mark twain',
    'Charles Darwin',
    'Alastair Reynolds',
    'Adam Rutherford',
    'David Quammen',
    'Sam Harris',
]

with open("sampleQuotesSemiProcessed.md", "w") as quotesFile:
    for quote in quotes.split('*quote*'):
        quote = quote.strip()
        lines = quote.splitlines()
        #remove empty rows
        lines = [line for line in lines if len(line) > 0]
        #values for each quote
        quoteText: str = ''
        sourceText: str = ''
        noteText: str = ''
        linkText: str = ''
        authorText: str = ''
        #if the quote comes from an iOS copy we treat it differently
        if 'excerpt' in quote.lower():
            #then it's a quote from iOS
            #check for authors
            for author in knownAuthors:
                if author.lower() in quote.lower():
                    authorText = author.title()
            nextLineIsSource = False #set to true when we see 'excerpt from'
            for count,line in enumerate(lines):
                line = line.strip()
                if count == 0:
                    #assume quote main text
                    quoteText = line
                if "Excerpt from".lower() in line.lower():
                    #iterate to get to source line
                    nextLineIsSource = True
                elif nextLineIsSource:
                    sourceText = line
                    nextLineIsSource = False
                if 'http' in line:
                    linkText = line
            if not quoteText == '':
                quotesFile.write(f'*quote:*\t{quoteText}\n',)
                quotesFile.write(f'*source:*\t{sourceText}\n',)
                quotesFile.write(f'*author:*\t{authorText}\n',)
                quotesFile.write(f'*link:*\t{linkText}\n',)
                quotesFile.write(f'*note:*\t{noteText}\n\n',)
                # print(
                #     f'*quote:*\t{quoteText}\n',
                #     f'*source:*\t{sourceText}\n',
                #     f'*author:*\t{authorText}\n',
                #     f'*link:*\t{linkText}\n',
                #     f'*note:*\t{noteText}\n\n',
                #     sep=''
                # )
                    
        else:
            #it is not a quote from iOS
            for count,line in enumerate(lines):
                if len(line) == 0:
                    break
                if count == 0:
                    #assume quote main text
                    quoteText = line
                elif count == 1:
                    #assume source
                    sourceText = line
                elif count == 2:
                    #assume note
                    noteText = line
                elif 'http' in line:
                    linkText = line
                for author in knownAuthors:
                    if author.lower() in line.lower():
                        authorText = author.title()
                        sourceText.replace(authorText,'')
                #check for authors
            if not quoteText == '':
                quotesFile.write(f'*quote:*\t{quoteText}\n',)
                quotesFile.write(f'*source:*\t{sourceText}\n',)
                quotesFile.write(f'*author:*\t{authorText}\n',)
                quotesFile.write(f'*link:*\t{linkText}\n',)
                quotesFile.write(f'*note:*\t{noteText}\n\n',)
                # print(
                #     f'*quote:*\t{quoteText}\n',
                #     f'*source:*\t{sourceText}\n',
                #     f'*author:*\t{authorText}\n',
                #     f'*link:*\t{linkText}\n',
                #     f'*note:*\t{noteText}\n\n',
                #     sep=''
                # )
# %%
