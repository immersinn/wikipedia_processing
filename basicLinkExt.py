"""See 'nlppipeline/test_files/runme_basicLinkExt.py' for example"""

import re
from wikipedia_processing import wikiDocProcess


def extractWikiLinksFromDoc(doc):
    """
    Pass in a Wikipedia article (a 'doc') in str or unicode format.
    This code splits the doc into sections, filters out "junk" sections,
    and extracts the links to other Wikipedia pages from the page.

    A dictionary of links is returned.  Each key is a section.  Each
    value is a list of dictionaries for links in the section. Each link
    contains:the Wikipedia page / object linked to, the section of the page
    linked to (if any), and the type of page / object linked to (page,
    file, etc.).

    Additionally, a new document content dictionary is returned.  Keys
    are section headings again, and values is a string of the new content,
    where Wikipedia links have been replaced with the link text
    associated with them.

    Note:  some link text contains the wiki hash ('#') meant to convey
    a subsection of the article. Typically this is hidden, and contained
    only in the link itself. E.g., see "Atomic orbital" article, section
    "Electron placement and the periodic table".  Link to
    "Electron_configuration#Atoms: Aufbau..."

    :type doc: str, unicode
    :param doc: a Wikipedia article

    :rtype: dict
    :rparam: see above
    """
    global title
    title = doc['title']
    
    parsed = wikiDocProcess.splitParsedPage(doc, verbose=False)
    filtered = wikiDocProcess.filterSections(parsed)
    sec_cont_dict = {}
    sec_link_dict = {}
    for section in filtered:
        new_content, new_links = extractWikiLinks(section['content'],
                                                  link_list = [])
        sec_cont_dict[section['header']] = new_content
        sec_link_dict[section['header']] = new_links

    return {'document':doc,
            'content':sec_cont_dict,
            'links':sec_link_dict}
    


def extractWikiLinks(cont, link_list=[]):
    """
    > Look through str/unicode for Wiki-to-Wiki links.
    > Account for imbedded links by counting the number of
    opening ([[) and closing (]]) observed.
    > When maximal link found, pass to 'processWikiLinks' to
    extract information about links.
    > Recursion

    :type cont: str, unicode
    :param cont: complete Wikipedia page / object content

    :type link_list: list
    :param link_list: current list of links extracted from section

    :rtype: tuple of (str, list)
    :rparam new_cont: section content with Wikipedia page / obejcts
    replaced with the respective text displayed for each link
    :rparam link_list: list of dictionaries with information about
    each link currently found in the section.  Contains keys:
    'link' (Wikipedia page / obejct title linked to);
    'text' (link text displayed in article; equiv to text);
    'lType' (type of linke returned, e.g. 'page', 'file')
    
    """
    new_cont = ''
    i = 0
    f = 0
    start = -1
    while i < len(cont):
        try:
            if cont[i]=='[' and cont[i+1]=='[':
                if start < 0:
                    start = i
                i += 1
                f += 1
            elif start > -1:
                if cont[i] == ']' and cont[i+1] == ']':
                    i += 1
                    f -=1
                    if f == 0:
                        sub_cont = cont[start:i+1]
                        sub_cont, link_list =\
                                  processWikiLinks(sub_cont,
                                                   link_list)
                        new_cont = ''.join([new_cont, sub_cont])
                        start = -1
            else:
                new_cont = ''.join([new_cont, cont[i]])
            i += 1
        except IndexError:
            i = len(cont)+1
    return new_cont, link_list


def processWikiLinks(cont, link_list):
    """
    > Parse link.
    > Identify link string.
    > Identify text string (if present).  Look for nested links
    in text string.  If found, pass to 'extractWikiLinks'.
    > Recursion

    :type cont: str, unicode
    :param cont: complete Wikipedia page / object content

    :type link_list: list
    :param link_list: current list of links extracted from section

    :rtype: tuple of (str, list)
    :rparam text: link text displayed in article
    :rparam link_list: list of dictionaries with information about
    each link currently found in the section.  Contains keys:
    'link' (Wikipedia page / obejct title linked to);
    'text' (link text displayed in article; equiv to text);
    'lType' (type of linke returned, e.g. 'page', 'file')
    """
    cont = cont.strip('[[').strip(']]')
    split_count = 0
    start = 0
    i = 0
    link = ''
    text = ''
    while i < len(cont):
        if cont[i] == '|':
            if split_count == 0:
                link = cont[:i]
            split_count += 1
            start = i + 1
            i += 1
        elif cont[i] == '[':
            new_cont, link_list =\
                      extractWikiLinks(cont[start:],
                                       link_list)
            text = new_cont
            i = len(cont)
        else:
            i += 1
    if not link:
        link = cont
    lType = getLinkType(link)
    link = postProcessLink(link)
    text = postProcessText(text, cont, split_count, start)
    link_list.append({'link':link,
                      'text':text,
                      'lType':lType})
    return text, link_list


def getLinkType(link):
    """
    Determine the type of Wikipedia page / object being linked to

    :type link: str, unicode
    :param link: Wikipedia page / object link

    :rtype lType: str
    """
    img_match = re.compile(r'\.jpg|\.png')
    if link.lower().startswith('file:'):
        lType = 'file'
    elif re.search(img_match, link.lower()):
        lType = 'file'
    elif link.lower().startswith('media:'):
        lType = 'media'
    elif link.lower().startswith('special:'):
        lType = 'special'
    elif link.lower().startswith('wictionary:'):
        lType = 'wictionary'
    else:
        lType = 'wikipage'
    return lType


def postProcessLink(link):
    """
    Get Wikipedia article and article linked to

    :type link: str, unicode
    :param link: Wikipedia page / object link

    :rtype: dict
    :rparam: contains the Wikipedia page name under key "article"
    and section of the page referenced (if applicable) in "section";
    both are type str, unicode
    """
    sub_article = []
    section = ''
    i = 0
    while i < len(link):
        if link[i]==':':
            sub_article = []
            i += 1
        elif link[i]=='#':      ## some issue here...
            if not sub_article:
                sub_article = [title]
            else:
                # find next special character
                j = i + 1
                section = ''
                while j < len(link):
                    if link[j] not in [']', '|', ',', ':',]:
                        section = ''.join([section, link[j]])
                        j += 1
                    else:
                        i = len(link)
                        break
            break                        
        else:
            sub_article.append(link[i])
            i += 1
    # issues with this (but super rare):
    # set([u'Apollo Command/Service Module', u'ISO/IEC 646', u'CP/M', u'ISO/IEC 8859', u'OS/2', u'A/UX', u'North American Man/Boy Love Association', u'OS/8', u'Radio Free Europe/Radio Liberty', u'HER2/neu', u'V/STOL', u'Mediaset'])
    article = ''.join(sub_article)
    article = article.split('/')[0]
    return {'article':article,
            'section':section}


def postProcessText(text, cont, split_count, start):
    """

    :type text: str, unicode
    :param text: Wikipedia page / object link text

    :type cont: str, unicode
    :param cont: complete text associated with Wikipedia page / object link
    
    :type start: int
    :param start: current index of cursor along link content, "cont"

    :rtype text: str, unicode
    """
    if not text:
        if start==len(cont):
            if split_count==0:
                text = cont
            else:
                if cont.find(',') > -1:
                    text = cont.split(',')[0]
                elif cont.find('(') > -1:
                    text = cont.split('(')[0]
                elif cont.find(':') > -1:
                    text = cont.split(':')[1]
        else:
            text = cont[start:]
    return text
