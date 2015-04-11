import re
import sys

from nlppipeline.corpus_doc.nlpdocs import NLPPrepBasic

BAD_HEADER_LIST = ['external links',
                   'see also',
                   'notes',
                   'footnotes',
                   'references',]


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
    parsedText = splitParsedPage(doc, verbose=False)
    parsedText = filterSections(parsedText)
    text = [pT['content'] for pT in parsedText]
    text = filter(None, text)
    while i < len(text):
        line = text[i]
        nlpline = NLPPrepBasic(content=line)
        nlpline.getWords()
        nt = parseWikiText(nlpline.words)
        i += 1
        newtext.append(nt)
    newtext = filter(None, newtext)
    return newtext


######################################################################
#{ Page Parser, section filter
######################################################################


def splitParsedPage(parsedpage, verbose=True):
    """
    Takes a parsed page dictionary, and divides it into several pieces.
    Specifically, all page "meta data" (read: non-text data) is placed
    in a single dictionary to be written to MDB, while the textual part
    of the page is split into paragraphs
    """
    sectionReMatch = re.compile(r'^==(?!=)(.+)==$')
    text = parsedpage['revision']['text']
    title = parsedpage['title']
    parsedPageList = []
    curcont = []
    header = 'FrontMatter'
    for t in text:
        mat = re.match(sectionReMatch, t)
        if mat:
            if header=='FrontMatter':
                fm, curcont = cleanFrontMatter(curcont)
                try:
                    fm = '\n'.join(fm)
                except TypeError:
                    print fm
                    print title
                    raise TypeError
                parsedPageList.append({'header':header,
                                       'content':fm})
                header = 'INTRO'
            curcont = '\n'.join(curcont)
            parsedPageList.append({'header':header,
                                   'content':curcont})
            header = mat.groups()[0]
            curcont = []
        else:
            curcont.append(t)
    curcont = '\n'.join(curcont)
    parsedPageList.append({'header':header,
                           'content':curcont})
    total_sections = len(parsedPageList)
    if verbose:
        print('Total number of sections for %s: %s' \
              % (title, total_sections))
    if total_sections==1:
        parsedPageList.append({'header':'Content',
                               'content':curcont})
    return parsedPageList


def cleanFrontMatter(content):
    content = filter(None, content)
    fm = []
    curcont = []
    i = 0; j = i
    while i < len(content):
        line = content[i]
        if line.startswith("[["):
            otherinfo = processwikiother(content, i)
            if otherinfo['i']==i:
                for j in range(i,len(content)):
                    curcont.append(content[j])
                i = j+1
            else:
                fm.append(otherinfo['text'])
                i = otherinfo['i']
        elif line.startswith("{{"):
            junkinfo = processwikijunk(content, i)
            if junkinfo['i']==i:
                for j in range(i,len(content)):
                    curcont.append(content[j])
                i = j+1
            else:
                fm.append(junkinfo['text'])
                i = junkinfo['i']
        elif line.startswith("==") and line.endswith("=="):
            curcont.append(line)
            for j in range((i+1),len(content)):
                curcont.append(content[j])
            i = j+1
        else:
            for j in range(i,len(content)):
                curcont.append(content[j])
            i = j+1
    return fm, curcont


def filterSections(sections):
    sections = filter(checkSectionHeader, sections)
    if len(sections)==1 and sections[0]['header']=='FrontMatter':
        sections = [{'header':'Content',
                     'content':sections[0]['content']}]
    else:
        sections = [s for s in sections if s['header']!='FrontMatter']
    return sections


def checkSectionHeader(section):
    """
    Filter function for determining if section
    looks like it contains useful text content by looking at the
    header (e.g. "References" would not be a good header).
    Return bool
    """
    header = section['header']
    header = header.lower()
    if header in BAD_HEADER_LIST:
        return False
    else:
        return True


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
            processed = processSquigs(i, words, new_words)
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


def processSquigs(i, words, new_words):
    """
    Single or double "{"?

    colorandhigh
    """
    if words[i+1]=="{":
        if words[i+2] in ['color', 'Font', 'color|']:
            processed = colorandhigh(words,i)
            processed['new_words'] = new_words
        else:
            processed = processrefs(words,
                                    i,
                                    new_words)                
    elif words[i+1]=="|":
        processed = processtables(i,
                                  words=words)
        processed['new_words'] = new_words
    elif words[(i-3):i]==['&', 'gt', ';']:
        processed = processrefs(words,
                                i,
                                new_words)
    else:
        processed = processSquig(words,i)
        processed['new_words'] = new_words
    return processed 


def processBracket(i, words):
    """
    Single or double "["?.  Single indicates some
    external links, double is a ref to another
    wikipedia page.
    """
    if words[i+1]=="[":
        processed = processwikilinks(words, i)
    else:
        processed = processextlinks(words, i)
    return processed


def processLeft(i, words):
    """
    Some type of html mark-up
    """
    # find closing </phrase>
    # pass phrase to markuptext
    pass
##    return processed


######################################################################
#{ Extra-text content processing
######################################################################

def processMultiLine(doclines, i, char='junk'):
    if char=='junk':
        ssearch = re.compile(r'\{\{')
        esearch = re.compile(r'\}\}')
        endchar = "}}"
        builddict = lambda x: buildwikijunkdict(x)
    elif char=='table':
        ssearch = re.compile(r'\{\|')
        esearch = re.compile(r'\|\}')
        endchar = "|}"
        builddict = lambda x: buildwikitabledict(x)
    elif char=='other':
        ssearch = re.compile(r'\[\[')
        esearch = re.compile(r'\]\]')
        endchar = "]]"
        builddict = lambda x: buildwikiotherdict(x)
    sbrack = [re.findall(ssearch, d) for d in doclines[i:]]
    ebrack = [re.findall(esearch, d) for d in doclines[i:]]
    scount = len(filter(None, sbrack[0]))
    ecount = len(filter(None, ebrack[0]))
    start = i
    k = 0
    try:
        while scount > ecount:
            k += 1
            scount += len(filter(None, sbrack[k]))
            ecount += len(filter(None, ebrack[k]))
    
        if doclines[i+k]==endchar:
            linesubset = doclines[start:(i+k+1)]
        elif doclines[i+k].endswith(endchar):
            linesubset = doclines[start:(i+k+1)]
        elif doclines[i+k].startswith(endchar):
            split = doclines[i+k].split(endchar, 1)
            doclines[i+k] = split[1]
            doclines.insert(i+k, endchar)
            linesubset = doclines[start:(i+k+1)]
        else:
            '''Bracket must be in text'''
            k = -1
            linesubset = []
        junkdict = builddict(linesubset)
        i = i+k+1
    except IndexError:
        stop = len(doclines)
        for line in reversed(doclines):
            if line.strip().endswith(endchar):
                break
            else:
                stop -= 1
        linesubset = doclines[start:stop]
        junkdict = builddict(linesubset)
        i = stop + 1
    
    return {'dict':junkdict,
            'text':'\n'.join(linesubset),
            'i':i,}


def processwikijunk(doclines, i):
    """
    Don't want to deal with this shit at the moment.  Run
    "last", remove it all...


    {{As of|YYYY|M|df=us|lc=y}} --> As of April 2009

    lists: line starts with
        "*"
        "#" (numbered lists)
    variations on nesting for these (e.g., "**")

    pairings
        "{{..."
        ...
        "}}"
    are also some sort of thing; image inserts, etc.

    Summary info:
        "{{Infobox (book|movie|...) ..."
        "| name = Dune",
        ...
        "| country = [[United States]]",  #note this is a link
        ...
        "}}"
    """
    out = processMultiLine(doclines, i, char='junk')
    return out


def processtables(i, doclines=[], words=[]):
    """
    Multiline

    http://en.wikipedia.org/wiki/Help:Table
   look for:
       "{| class=&quot;wikitable&quot;"
        ...
        "|}"

    actually, look for any
        "{| ..."
        ...
        "|}"
    pairings.  This seems to be markup for any tables, inserts, etc.

    Using HTML elements: <table>, <tr>, <td> or <th>
    """
    if doclines:
        tabledict = processtableLines(doclines, i)
        return tabledict
    elif words:
        contentdict = {}
        start = i + 2
        stop = findendoftable(words, start)
        tablecontent = words[start:(stop-1)]
        contentdict['i'] = stop+1
        contentdict['content'] = []
        return contentdict


def processtablesLines(doclines, i):
    out = processMultiLine(doclines, i, char='table')
    return out


def processwikiother(doclines, i):
    if doclines[i].endswith("]]"):
        '''These are typically category notes when appearing
        as a separate line.  Can also be links.'''
        catinfo = processcategories(doclines[i])
        return {'text':doclines[i],
                'i':i+1}
    else:
        out = processMultiLine(doclines, i, char='other')
        return out


def processcategories(docline):
    """
    Apply a category label to an article (categories can be concepts
    too, go on brush your shoulders off...)

    [[(:)?Category:<Category Name>(|)?]]
        <-- Omitting leading ":" shows no text
        <-- Placing the leading ":" d/n place article in category, but show link
    """
    pat = re.compile(r'(:)?Category:([a-zA-Z0-9 ]+)(\|)?]]')
    mat = re.search(pat, docline)
    if mat:
        groups = mat.groups()
        if not groups[0] and not groups[2]:
            return {'Type':'Categorize',
                    'Category':groups[1]}
        else:
            return {'Type':'Link',
                    'Category':groups[1]}
    else:
        return {}


def buildwikijunkdict(lines, returnNone=True):
    """
    Construct a dictionary representing the table composed of
    the lines in 'lines'.
    """
    if returnNone:
        return {}
    else:
        return lines


def buildwikitabledict(lines, returnNone=True):
    """
    Construct a dictionary representing the table composed of
    the lines in 'lines'.
    """
    if returnNone:
        return {}
    else:
        return lines


def buildwikiotherdict(lines, returnNone=True):
    """
    Construct a dictionary representing the table composed of
    the lines in 'lines'.
    """
    if returnNone:
        return {}
    else:
        return lines


def removeotherjunk(docline):
    """
    Remove stuff like
    <score>...</score>
    """
    pass


######################################################################
#{ Within text content processing
######################################################################


def mainarticlelinks(docline):
    """
    "{{main|A (disambiguation)}}"
    """
    pass


def processSquig(words, i):
    contentdict = {}
    start = i + 1
    stop = findendofref(words, start, kind='single')
    contentdict['i'] = stop+1
    contentdict['content'] = []
    return contentdict


def processwikilinks(words, i, extract=['text']):
    """
    Typically in-line

    # Standard (using '|' referred as 'piping')
    [[<Article Name>]]
    [[<Article Name>|<text to show>]]

    # Using trailing "|" to hide text
    [[kingdom (biology)|]] # biology not shown
    [[Seattle, Washington|]] #Washington not shown
    [[Wikipedia:Village pump|]] #Wikipedia hidden

    # Blending
    [[bus]]es # links to 'bus' article, hyperlink text is 'buses'
    [[micro-]]<nowiki/>second # hypertext is 'micro', word is 'micro-second'

    # Link to sections (can also pipe)
    [[Wikipedia:Manual of Style#Italics]] # MoS page, 'Italics' section
    [[#Links and URLs]] # link to section on same page

    # Other language
    [[<language abriv>:<Article Name>]]

    # Another wikimedia site
    [[Wiktionary:fr:bonjour]]  # standard modification apply

    # Media
    [[media:<media file>|<Display Text>]]

    #Images
    [[File:<wiki file path>|link=Wikipedia|...|...]]

    # Special shit
    [[Special:BookSources/<ISBN>|alt text]] --> links to a book by isbn
    [[Special:WhatLinksHEre/aaa]]
    [[Special:SpecialTag/stuff(|more stuff)?]]

    want to iterativerly find all of them and replace them with
    appropriate text, as well as record the outgoing link

    Should links to other pages be given special notation?  I.e., are
    concepts "words"? 
    """
    def getLinkText(linkcontent):
        text = []
        i = len(linkcontent)-1
        while i >= 0:
            if linkcontent[i]=='|':
                if text:
                    break
                else:
                    i -= 1
            elif linkcontent[i].startswith("|"):
                text.append(linkcontent[i].strip("|"))
                break
            elif "|" in linkcontent[i]:
                text.append(linkcontent[i].split("|")[-1])
                break
            else:
                text.append(linkcontent[i])
                i -= 1
        text = [t for t in reversed(text)]
        return text


    def getLinkArticle(linkcontent):
        #umm....this isn't working, yo
        #sometimes start word not split from rest..
        ignorelist = ['special', 'media', 'file', 'wictionary']
        for phrase in ignorelist:
            if linkcontent[0].lower().startswith(phrase):
                return 'IGNORE'
        article = []
        i = 0
        while i < len(linkcontent):
            if linkcontent[i]=='|':
                break
            elif linkcontent[i].startswith("|"):
                break
            elif "|" in linkcontent[i]:
                pipesplit = linkcontent[i].split("|")
                article.append(pipesplit[0])
                break
            elif linkcontent[i]==':':
                article = []
                i += 1
            elif linkcontent[i]=='#':
                if not article:
                    article = ['SELF']
                break                        
            else:
                article.append(linkcontent[i])
                i += 1

        if not article:
            print(linkcontent)
            return ''
        else:
            return postprocess(article)


    def postprocess(article):
        # Athens , Kentucky --> Athens, Kentucky
        # Issue with capitilization
        # issues with ( word ) --> (word)
        # [u':', u'an', u':', u'|Aragonese', u'Wikipedia']
        if article[-1] in ['!',] and len(article)>1:
            article[-2] = ''.join(article[-2:])
            article = article[:-1]
        if '(' in article and ')' in article:
            left = article.index('(')
            right = article.index(')')
            if right-left==1:
                article[left] = '()'
            elif right-left==2:
                article[left] = ''.join(article[left:(right+1)])
                for i in reversed(range(left+1,right+1)):
                    article.pop(i)
            elif right-left>2:
                article[left] = ''.join(article[left:(left+2)])
                article[right] = ''.join(article[(right-1):(right+1)])
                article.pop(right-1)
                article.pop(left+1)
            
        article = ' '.join(article)
        # issues with this (but super rare):
        # set([u'Apollo Command/Service Module', u'ISO/IEC 646', u'CP/M', u'ISO/IEC 8859', u'OS/2', u'A/UX', u'North American Man/Boy Love Association', u'OS/8', u'Radio Free Europe/Radio Liberty', u'HER2/neu', u'V/STOL', u'Mediaset'])
        article = article.split('/')[0]
        return article


    contentdict = {}
    start = i + 2
    stop = findendoflink(words, start)
    linkcontent = words[start:(stop-1)]
    contentdict['i'] = stop+1
    
    if linkcontent:
        if 'text' in extract:
            contentdict['text'] = getLinkText(linkcontent)
            contentdict['content'] = contentdict['text']
        if 'link' in extract:
            contentdict['link'] = getLinkArticle(linkcontent)
    else:
        contentdict['text'] = ''
        contentdict['link'] = ''
        contentdict['content'] = ''

    return contentdict        


def processrefs(words, i, new_words, extract=[]):
    """
    def removereferences(docline):
        <Comment>
        Different types. Same closing, different opening
            &lt;ref&gt;{{harvnb|Gelb|Whiting|1998|p=45}}&lt;/ref&gt;
            &lt;ref name=&quot;batson3&quot;&gt;[Batson, C. (2011). Altruism in humans. New York, NY US: Oxford University Press.]&lt;/ref&gt;
        General:
            &lt;ref ... &lt;/ref&gt;
        <Comment>
        pass
    """
    contentdict = {}
    if words[i+1]=="{":
        start = i + 2
        stop = findendofref(words, start)
    else:
        start = i + 1
        stop = findendofref(words, start, kind='single')
    refcontent = words[start:(stop-1)]
    if words[(i-7):i]==['&', 'lt', ';', 'ref', '&', 'gt', ';']:
        new_words = new_words[:-7]
        contentdict['i'] = stop+1+7
    elif words[(i-7):i]==['&', 'lt', ';', 'math', '&', 'gt', ';']:
        new_words = new_words[:-7]
        contentdict['i'] = stop+1+7
    elif words[(i-7):(i-4)]==['&', 'lt', ';'] and\
         words[(i-3):i]    ==['&', 'gt', ';']:
        new_words = new_words[:-7]
        contentdict['i'] = stop+1+7
    else:
        contentdict['i'] = stop+1
    if not extract:
        contentdict['content'] = []
    contentdict['new_words'] = new_words
    return contentdict


def processextlinks(words, i):
    """
    # Single bracketed URLs are understood as external links
    [http://www.wikipedia.org Wikipedia] # Link to wiki, text is 'Wikipedia'
    [http://www.wikipedia.org] # Link to wiki, auto-numbered text, '[1]'

    # If you're a dick...
    <span class="plainlinks">[http://www.wikipedia.org Wikipedia]</span> # Same as 1st

    # 'bare' links also allowed

    # Also double braces; just exclude these, let wikijunk handle
    {{<Oh God lots of special shit>:<text of some sort fuck>}}

    # Just to cover my bases...
    http(s)?://
    irc(s)?://
    ftp://
    news://
    mailto://
    gopher://
    """
    if words[i]=="[":
        start = i + 1
        stop = findendoflink(words, start, kind='single')
        contentdict = {'content':[],
                       'i':stop+1}
    else:
        contentdict = {'content':[],
                       'i':i+1}
    return contentdict


def colorandhigh(docwords, i):
    """
    Just extract the 'sample text here' and replace formatting
    with text alone.
    {{color|<color>|sample text here}} <-- different color
    {{Font color||<color>|sample text here}} <-- highlight
    """
    start = False
    count = 0
    i += 2
    text = []
    tcount = 3 if docwords[i]=="Font" else 2
    while True:
        if start:
            if docwords[i]=="}":
                i += 2
                break
            else:
                text.append(docwords[i])
                i += 1
        elif docwords[i]=="|":
            count += 1
            if count==tcount:
                start = True
            i += 1
        elif docwords[i].startswith("|"):
            count += 1
            if count==tcount:
                start = True
                text.append(docwords[i].strip("|"))
            i += 1
        elif docwords[i].endswith("|"):
            count += 1
            if count==tcount:
                start = True
            i += 1
        else:
            i += 1
    return {'content':text,
            'i':i}


def findendoflink(words, i, kind='double'):
    if kind=='double':
        while not words[i-1]=="]" or not words[i]=="]":
            i += 1
        return i
    elif kind=='single':
        while not words[i]=="]":
            i += 1
        return i


def findendofref(words, i, kind='double'):
    if kind=='double':
        while not words[i-1]=="}" or not words[i]=="}":
            i += 1
        return i
    elif kind=='single':
        while not words[i]=="}":
            i += 1
        return i


def findendoftable(words, i):
    while not words[i-1]=="|" or not words[i]=="}":
        i += 1
    return i


def markuptext(docline):
    """
    <u>...</u>
    <del>...</del>
    <ins>...</ins>
    <nowiki>
        ...
    </nowiki>

    <span ...>...</span>
    """
    pass


