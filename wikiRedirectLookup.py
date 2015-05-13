import time

from wikiMDBPageIterator import (WikiPageIteratorAll,
                                 redirectpage,
                                 disambiguationpage,
                                 datepage,
                                 emptypage,
                                 filepage,
                                 connectMon)
##from wikidocprocess import processwikilinks


def createWikiRedirectDictAndIgnoreList(limit=100,
                                        verbose=True):
    redirectDict = {}
    ignoreList = []
    pages = WikiPageIteratorAll(limit=limit)
    for i, page in enumerate(pages):
        if i%50000==0 and verbose:
            print('On page %s: %s' %(i,page['title']))
        if redirectpage(page):
            redirectDict[page['title']] = getRedirectPage(page)
        elif disambiguationpage(page):
            ignoreList.append(page['title'])
        elif datepage(page):
            ignoreList.append(page['title'])
        elif emptypage(page):
            ignoreList.append(page['title'])
        elif filepage(page):
            ignoreList.append(page['title'])
    pages.conn.close()
    return redirectDict, set(ignoreList)


def getRedirectPage(wikidoc):
    text = wikidoc['revision']['text']
    text = text.strip()
    text = text[9:] # Remove #REDIRECT (upper or lower or mixed)
    text = text.strip()
    if text:
        text = text.split(']]')[0]
        text = text.strip('[[').split()
        text.insert(0,'['); text.insert(0, '[')
        text.extend([']',']'])
        link = processwikilinks(text, 0, extract=['link'])['link']
    else:
        link = None
    return link


def connect2SpecialPages():
    """
    Creates connections to MDB database for ignore list and
    redirect dict.  Returns connectMon objects, one for each

    :type redirect: connectMon.MongoConn
    :param redirect: mongo db connection to the redirect collection
    in the WikiData MDB db

    :type ignore: connectMon.MontoConn
    "param ignore: mongo db connection to the ignore collection
    in the WikiData MDB db
    """
    ignore = connectMon.MongoConn()
    redirect = connectMon.MongoConn()
    ignore.makeDBConn('WikiData')
    redirect.makeDBConn('WikiData')
    ignore.makeCollConn('wikiSpecialPages.ignoreList')
    redirect.makeCollConn('wikiSpecialPages.redirectDict')
    return redirect, ignore


def getSpecialPages():
    """
    Call this method to retrieve the two MDB datasets:
    redirect dictionary and pages-to-ignore list
    """
    Rmdb, Imdb = connect2SpecialPages()
    redirectDict = {e['page'] : e['redirect']\
                    for e in Rmdb.coll.find()}
    ignoreList = [e['page'] for e in Imdb.coll.find()]
    Rmdb.conn.close()
    Imdb.conn.close()
    return {'redirectDict':redirectDict,
            'ignoreList':ignoreList}


def dict2mdb(curDict):
    """Turns a python dict object into a list to throw to mdb"""
    mdblist = [{'page':k, 'redirect':v} for k,v in curDict.items()]
    return mdblist


def list2mdb(curList):
    """Takes a python list of pages, and turns into a list of dicts
    for insertion into MDB"""
    mdblist = [{'page':k} for k in curList]
    return mdblist


def main(limit=100, tomdb=True, returnvals=False):
    """
    Primary method for iterating over articles in Wiki MDB
    database and determining which ones to ignore, and which
    are redirect page.

    Create MDB entries for ipages to ignore, and redirect
    pages + how they redirect.
    """
    start = time.time()
    if tomdb:
        print('Getting MDB connections...')
        redirectmdb, ignoremdb = connect2SpecialPages()
    print('Creating look-up tables for special pages...')
    redirectDict, ignoreList =\
                  createWikiRedirectDictAndIgnoreList(limit=limit)
    elapsed = time.time() - start
    print('Time elapsed: %s' % elapsed)
    if tomdb:
        print('Writing data to mdb...')
        redirectmdb.MongoInsert(dict2mdb(redirectDict))
        ignoremdb.MongoInsert(list2mdb(ignoreList))
        redirectmdb.conn.close()
        ignoremdb.conn.close()
    if returnvals:
        return {'redirectDict':redirectDict,
                'ignoreList':ignoreList}
##    out = getSpecialPages()
##    R = out['redirectDict']
##    I = out['ignoreList']
##    print(I[:10])
##    print(R.items()[:10])


if __name__=="__main__":
    print("Startng process:")
    main(limit=0)
    print("Fine!")
