import sys
sys.path.append('/Users/immersinn/Dropbox/PythonCode/')
from wikiprep import wikidocprocess
from NLP.nlp_extraction_tools import NLPPrepBasic


######################################################################
#{ Primary pre-processing function for body text
######################################################################


def preprocessWikiText(doc):
    """
    Now, parse through lines and use a decision tree to determine
    how to interpret / parse document...

    Looks for beginning of "phrases" to initialize parse element

    need to track nested stuff as well...
    """
    newtext = []
    i = 0
    parsedText = wikidocprocess.splitParsedPage(doc, verbose=False)
    parsedText = wikidocprocess.filterSections(parsedText)
    text = [pT['content'] for pT in parsedText]
    text = filter(None, text)
    while i < len(text):
        line = text[i]
##        if line.startswith("{{") and line.endswith("}}"):
##            # don't keep for now
##            # wikidocprocess.wikijunkprocess
##            i += 1
##        elif line.startswith("[["):
##            if line.endswith("]]"):
##                '''These are typically category notes when appearing
##                as a separate line.  Can also be links.'''
##                catinfo = wikidocprocess.processcategories(line)
##                nt = catinfo
##                i += 1
##            else:
##                otherinfo = wikidocprocess.processwikiother(text, i)
##                nt = otherinfo['text']
##                i = otherinfo['i']
##        elif line.startswith("{{"):
##            junkinfo = wikidocprocess.processwikijunk(text, i)
##            nt = junkinfo['text']
##            i = junkinfo['i']
##        elif line.startswith("==") and line.endswith("=="):
##            # section header / subheader
##            # don't keep for now
##            i += 1
##        else:
        nlpline = NLPPrepBasic(content=line)
        nlpline.getWords()
        nt = parseWikiText(nlpline.words)
        i += 1
        newtext.append(nt)
    newtext = filter(None, newtext)
    return newtext


######################################################################
#{ For processing textual content in article
######################################################################


def parseWikiText(words):
    """
    For lines in main text that appear to be content text, parse
    throgh and remove special references, characters, etc., and
    replace with appropriate content, as specified in
    'wikidocprocess'.

    Aviod using 're' where possible.
    """
    i = 0
    new_words = []
    while i < len(words):
        if words[i]=="{":
            processed = processSquig(i, words, new_words)
            new_words = processed['new_words']
            new_words.extend(processed['content'])
            i = processed['i']
        elif words[i]=="[":
            processed = processBracket(i, words)
            new_words.extend(processed['content'])
            i = processed['i']
        elif words[i]=="<": # check that this gets split away from letter
            i, nw = processLeft(i, words)
            new_words.append(nw)
        else:
            new_words.append(words[i])
            i += 1
    new_words = filter(None, new_words)
    return new_words


def processSquig(i, words, new_words):
    """
    Single or double "{"?

    colorandhigh
    """
    if words[i+1]=="{":
        if words[i+2] in ['color', 'Font', 'color|']:
            processed = wikidocprocess.colorandhigh(words,i)
            processed['new_words'] = new_words
        else:
            processed = wikidocprocess.processrefs(words,
                                                   i,
                                                   new_words)                
    elif words[i+1]=="|":
        processed = wikidocprocess.processtables(i,
                                                 words=words)
        processed['new_words'] = new_words
    elif words[(i-3):i]==['&', 'gt', ';']:
        processed = wikidocprocess.processrefs(words,
                                               i,
                                               new_words)
    else:
        processed = wikidocprocess.processSquig(words,i)
        processed['new_words'] = new_words
    return processed 


def processBracket(i, words):
    """
    Single or double "["?
    """
    if words[i+1]=="[":
        # find closing double bracket
        # pass phrase to wikilinks
        processed = wikidocprocess.processwikilinks(words, i)
    else:
        # find closing single bracket
        # externallinks
        processed = wikidocprocess.processextlinks(words, i)
    return processed


def processLeft(i, words):
    """
    Some type of html mark-up
    """
    # find closing </phrase>
    # pass phrase to markuptext
    pass
##    return processed
