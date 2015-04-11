# 0) Create a new mdb collection under the wiki db: link network
#       Each entry has 3 fields:
            # name:  title of page
            # out:   list of pages page links to
            # in:    list of pages linking to page
# 1) query mdb for all wiki docs
# 2) for each file:
    # i_   Get text body
    # ii_  Find all links to other wiki pages..
    # iii_ Write lisk of links back to mdb as 'Wikipedia Out Links'
# 3) use map-reduce over 'Wikipedia Out Links' to get number of links
#    going to each wikipedia page


# need to account for recirect links --> change links to redirect
# pages to the page they're redirected to...
import time
import pickle

from nltk import word_tokenize
import re

from wikiMDBPageIterator import WikiPageIterator, connectMon
import wikidocprocess
from wikiRedirectLookup import getSpecialPages

import basicLikExt


def buildOutLinkDict(pi, spt):
    """
    Parses through a wikipedia page, gets all internal (wiki-to-wiki) links,
    corrects redirect links, removes links we're ignoring

    :type pi: wikiMDBPageIterator.WikiPageIteratorAll
    :param pi: Iterates over all wikipedia pages in the WikiData db

    :type spt: function / method
    :param spt: This is the "filter" function that utilizes the redirectDict
    and ignoreList to edit the link list.  Page titles that are rediredt to
    others on Wikipedia are replaced with the titles they redirect to. Page
    titles that correspond to page types not being tracked are removed
    from the list.

    :type outLinkDict: dict
    :param outLinkDict: Dictionary of page outlinks.  Keys are source page title,
    values are list of linked-to pages.
    """
    stop = False
    outLinkDict = {}
    while not stop:
        try:
            doc = pi.next()
            title = doc['title']
            splitPage = wikidocprocess.splitParsedPage(doc)
            text = [pT['content'] for pT in splitPage]
            text = filter(None, text)
            linkMatch = re.compile(r'\[\[.+?\]\]')
            links = []
            for tex in text:
                links.extend(re.findall(linkMatch, tex))
            links = filter(None, links)
            pages = [wikidocprocess.processwikilinks(word_tokenize(link),
                                                     0,
                                                     extract=['link'])['link'] \
                     for link in links]
            pages = filter(None, list(set([spt(p) for p in pages])))
            outLinkDict[title] = pages
        except StopIteration:
            stop = True
    return outLinkDict


def buildInLinkDict(outLinkDict):
    titles = set(outLinkDict.keys())
    specialPages = getSpecialPages()
    redirectDict = specialPages['redirectDict']
    ignoreSet = set(specialPages['ignoreList'])
    inLinkDict = {k:[] for k in outLinkDict.keys()}
    for page, links in outLinkDict.items():
        for l in links:
            if l in titles:
                inLinkDict[l].append(page)
            else:
                inLinkDict[l] = [page]
    return inLinkDict


def mergeLinkDicts(outLinkDict, inLinkDict):
    titles = set(outLinkDict.keys()).union(set(inLinkDict.keys()))
    numtitles = len(titles)
    print('Total referenced pages: %s' % numtitles)
    linkDict = {t:{} for t in titles}
    for i,t in enumerate(titles):
        if i%5000==0:
            print('On title %s: %s' %(i,t))
        linkDict[t]['outLinks'] = outLinkDict[t] \
                                  if t in outLinkDict.keys() else []
        linkDict[t]['inLinks'] = inLinkDict[t] \
                                  if t in inLinkDict.keys() else []
    return linkDict


def dict2mdb(linkDict):
    mdblist = [{'title':k,'links':v} for k,v in linkDict.items()]
    return mdblist


def specialPagesTrans(redirectDict, ignoreList, title):
    """
    Takes a page title and determines if it's in either the
    redirect dictionary, or if it's an ignore page.  If in
    redirectDict, the "redirect to" page is returend.  If in
    the ignoreList, a blank title is returned.  Else, the
    input title is returned.
    """
    try:
        title = redirectDict[title]
    except KeyError:
        title = title
    finally:
        if title in ignoreList:
            title = ''
        return title
    

def main(limit=100, tomdb=True, returnvals=False):
    """
    Primary method for building the in / out link lists for
    Wikipedia pages.

    :type limit: int
    :param limit: determine the maximum number of pages to retrieve
    from MDB.  Setting to '0' retrieves all pages.

    "type returnvale: bool
    :param returnvals: set to 'True' to return created in / out
    link lists
    """
    start = time.time()
    if tomdb:
        print('Getting MDB connections...')
        wikimdb = connectMon.MongoConn()
        wikimdb.makeDBConn('WikiData')
        wikimdb.makeCollConn('wikiLinkStructure')
    print('Retrieving special pages from mdb...')
    out = getSpecialPages()
    R = out['redirectDict']
    I = set(out['ignoreList'])
    print('redirectDict and ignoreList retrieved!')
    pages = WikiPageIterator(limit=limit)
    print('Grabbing out links...')
    spt = lambda title: specialPagesTrans(R, I, title)
    outLinkDict = buildOutLinkDict(pages, spt)
    elapsed = time.time()-start
    print('Time elapsed: %s' % elapsed)
    print('Inferring in links...')
    inLinkDict = buildInLinkDict(outLinkDict)
    elapsed = time.time() - start
    print('Time elapsed: %s' % elapsed)
    print('Merging in and out link dicts...')
    linkDict = mergeLinkDicts(outLinkDict, inLinkDict)
    elapsed = time.time()-start
    print('Time elapsed: %s' % elapsed)
    print('Pickling dictionary...')
    F = open('/Users/immersinn/Dropbox/PythonCode/wikiprep/data/linksDict.pkl',
             'wb')
    pickle.dump(linkDict, F)
    F.close()
    print('Done pickling!')
    if tomdb:
        mdblist = dict2mdb(linkDict)
        print('Writing data to mdb...')
        wikimdb.MongoInsert(mdblist)
        elapsed = time.time()-start
    if returnvals:
        return linkDict
    print('Time elapsed: %s' % elapsed)


if __name__=="__main__":
    print('Starting process:')
    main(limit=0)
    print('Fine!')


"""
Total number of sections for Dambanang Kawayan: 8
Traceback (most recent call last):
  File "getWikiPageLinks.py", line 181, in <module>
    main(limit=0)
  File "getWikiPageLinks.py", line 152, in main
    outLinkDict = buildOutLinkDict(pages, spt)
  File "getWikiPageLinks.py", line 51, in buildOutLinkDict
    doc = pi.next()
  File "/Users/immersinn/Dropbox/PythonCode/wikiprep/wikiMDBPageIterator.py", line 48, in next
    doc = self.conn.LastQ.next()
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pymongo/cursor.py", line 1038, in next
    if len(self.__data) or self._refresh():
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pymongo/cursor.py", line 999, in _refresh
    limit, self.__id))
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pymongo/cursor.py", line 925, in __send_message
    self.__compile_re)
  File "/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/pymongo/helpers.py", line 97, in _unpack_response
    cursor_id)
pymongo.errors.CursorNotFound: cursor id '130407925070' not valid at server
"""
