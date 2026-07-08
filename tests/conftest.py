"""
Shared test fixtures for the adamsquotes package.

Provides sample markdown data used across multiple test modules.
"""

from __future__ import annotations

SAMPLE_MD = """*quote:*	Yeah Matt Damon saying "fortune favours the bold" certainly didn't favour SBF's victims.
*source:*	reddit r/perth
*author:*	Captain-Peacock
*link:*	https://www.reddit.com/r/perth/comments/zlcc45/gamblers_anonymous_warns_of_really_really_sad/j053yug/
*note:*

*quote:*	I felt overwhelmed by stimuli from within: thoughts.
*source:*	But You Dont Look Autistic
*author:*	Bianca Toeps
*link:*
*note:*	If autism is a sensory processing disorder, maybe adhd is just autism specifically for thoughts?

*quote:*	A more inclusive, more comprehensive explanation can be found in the Intense World Theory, a theory that has been gaining more credence in the past few years. The founders of this theory, neuroscientists Henry and Kamila Markram, have an autistic son.
*source:*	But You Dont Look Autistic
*author:*	Bianca Toeps
*link:*
*note:*
"""

SAMPLE_HEADER = """<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body>
    <div class="tableOfContentsDiv">
        <!-- table of contents -->
    </div>
    <div class="quotesDiv">
        <!--quotes-->
    </div>
</body>
</html>"""

RAW_INPUT = """*quote*
I felt overwhelmed by stimuli from within: thoughts.
But You Dont Look Autistic
If autism is a sensory processing disorder, maybe adhd is just autism specifically for thoughts?

*quote*
There, he earned his final footnote in history by befriending a fellow POW.
Neurotribes steve silberman

*quote*
"The gesture that precipitates this insight"

Excerpt from
Waking Up: A Guide to Spirituality Without Religion
Sam Harris
This material may be protected by copyright.

*quote*
I love it, because it's so strange, so dizzying.
https://www.robinsloan.com/newsletters/visions/#spotify

*quote*
"Things look different without the Prophets' lies clouding my vision." - To the Arbiter, on board of the Shadow of Intent.

*quote*
A lot of not quitting quotes are bullshit.
Michael Jordan quit college before he graduated.
Michael Jordan then quit basketball to play baseball.
https://www.reddit.com/r/GetMotivated/comments/5m7a3p/image_xkcd_shouldve_left_sooner/dc1qpwj/
"""

EXPECTED_OUTPUT = (
    "*quote:*\tI felt overwhelmed by stimuli from within: thoughts.\n"
    "*source:*\tBut You Dont Look Autistic\n"
    "*author:*\t\n"
    "*link:*\t\n"
    "*note:*\tIf autism is a sensory processing disorder,"
    " maybe adhd is just autism specifically for thoughts?\n"
    "\n"
    "*quote:*\tThere, he earned his final footnote in history"
    " by befriending a fellow POW.\n"
    "*source:*\tNeurotribes steve silberman\n"
    "*author:*\tSteve Silberman\n"
    "*link:*\t\n"
    "*note:*\t\n"
    "\n"
    '*quote:*\t"The gesture that precipitates this insight"\n'
    "*source:*\tWaking Up: A Guide to Spirituality Without Religion\n"
    "*author:*\tSam Harris\n"
    "*link:*\t\n"
    "*note:*\t\n"
    "\n"
    "*quote:*\tI love it, because it's so strange, so dizzying.\n"
    "*source:*\thttps://www.robinsloan.com/newsletters/visions/#spotify\n"
    "*author:*\t\n"
    "*link:*\thttps://www.robinsloan.com/newsletters/visions/#spotify\n"
    "*note:*\t\n"
    "\n"
    "*quote:*\t\"Things look different without the Prophets'"
    ' lies clouding my vision." - To the Arbiter,'
    " on board of the Shadow of Intent.\n"
    "*source:*\t\n"
    "*author:*\t\n"
    "*link:*\t\n"
    "*note:*\t\n"
    "\n"
    "*quote:*\tA lot of not quitting quotes are bullshit.\n"
    "*source:*\tMichael Jordan quit college before he graduated.\n"
    "*author:*\t\n"
    "*link:*\thttps://www.reddit.com/r/GetMotivated/comments/5m7a3p/"
    "image_xkcd_shouldve_left_sooner/dc1qpwj/\n"
    "*note:*\tMichael Jordan then quit basketball to play baseball.\n"
)
