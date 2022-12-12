'''
I want to somewhat automate the process of adding tags to the raw quotes.
Then I can manually go in and fix them up.

I have a raw quotes file: sampleQuotesUnprocessed.md
'''

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

for quote in quotes.split('\n\n')[1:4]:
    quote = quote.strip()
    lines = quote.splitlines()
    #if the quote comes from an iOS copy we treat it differently
    if 'excerpt' in quote.lower():
        #then it's a quote from iOS
        pass
    else:
        #it is not a quote from iOS
        for count,line in enumerate(lines):
            line = line.strip()
            if count == 0:
                #assume quote main text
                print(f'*quote:* {line}')
            elif count == 1:
                #assume source
                print(f'*source:* {line}')
            elif count == 2:
                #assume note
                print(f'*note:* {line}')
            elif 'http' in line:
                print(f'*link:* {line}')
# %%
