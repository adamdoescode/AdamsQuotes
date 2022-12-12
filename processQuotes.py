'''
A script to quickly process quotes from a markdown text file into a html file.
TODO Each quote will be contained within a div with a class of "quote".
TODO div elements will be boxes (TODO flexbox) with a border and padding.
TODO Each quote will have a class of "quote" and a unique id.
'''

#%%

with open("sampleQuotes.md", "r") as quotesFile:
    quotes = quotesFile.readlines()

# with open("quotes.html", "w") as htmlFile:
#     for quote in quotes:
#         htmlFile.write(f"

class ProcessQuotes:

    def __init__(self, quotes):
        self.quotes = quotes
    
    def FindTags(self):
        for quote in self.quotes:
            if quote.startswith("#"):
                print(quote)

    def processQuotes(self):
        for quote in self.quotes:
            print(quote)

    def writeQuotes(self):
        with open("quotes.html", "w") as htmlFile:
            for quote in self.quotes:
                htmlFile.write(f"")

# %%
