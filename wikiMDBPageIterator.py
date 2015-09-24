
from dbinterface_python.dbconns import connectMon


class WikiPageIteratorAll:
    """
    Connects to Wiki MDB; Creates a Cursor itterable over all docs up to limit;
    """

    def __init__(self, limit=100, skip=0):
        self.conn = getWikiMDBConn()
        self.cursor = self.conn.query(limit=limit, skip=skip,
                                      no_cursor_timeout=True)
        self.current = 0
        self.high = self.cursor.count(with_limit_and_skip=True)
        

    def __iter__(self):
        return self


    def reset(self):
        self.cursor.rewind()


    def next(self):
        if self.current >= self.high:
            raise StopIteration
        self.current += 1
        return self.cursor.next()
    

class WikiPageIterator(WikiPageIteratorAll):
    """
    Performs same function as 'WikiPageIteratorAll', but
    filters out pages deemed to be not of interest.
    """

    def next(self): # Python 3: def __next__(self)
        if self.current > self.high:
            raise StopIteration
        else:
            good_doc_status = False
            while not good_doc_status:
                self.current += 1
                if self.current==self.high:
                    raise StopIteration
                doc = self.cursor.next()
                if 'title' not in doc.keys():
                    doc['title'] = doc['dict']['title']
                if 'revision' not in doc.keys():
                    doc['revision'] = doc['dict'].pop('revision')
                if not badpage(doc):
                    good_doc = doc
                    good_doc_status = True
            return good_doc


def getWikiMDBConn(coll=''):
    """Establishes connection to MDB wiki collection"""
    
    wikimdb = connectMon.MongoConn()
    wikimdb.makeDBConn('WikiData')
    if not coll:
        wikimdb.makeCollConn('articleDump')
    else:
        wikimdb.makeCollConn(coll)
    return wikimdb


######################################################################
#{ Filters
######################################################################


def badpage(doc):
    """
    General check for if the document is a desirable one to
    do analysis with.
    """
    
    if emptypage(doc):
        return True
    elif redirectpage(doc):
        return True
    elif disambiguationpage(doc):
        return True
    elif datepage(doc):
        return True
    elif filepage(doc):
        return True
    else:
        return False


def redirectpage(wikidoc):
    text = wikidoc['revision']['text']
    if type(text) in [str, unicode] and\
       text.upper().startswith('#REDIRECT'):
        return True
##    elif len(text)==0:
##        return True
##    elif len(text)==1 and not text[0]:
##        return True
    else:
        return False


def disambiguationpage(wikidoc):
    title = wikidoc['title']
    title = title.strip()
    if title.endswith('(disambiguation)'):
        return True
    else:
        return False


def datepage(wikidoc):
    datePage = False
    text = wikidoc['revision']['text']
    for t in text[:10]:
        if t.strip().lower()=="{{day}}" or\
           t.strip().lower()=="{{this date in recent years}}":
            datePage = True
            break
    return datePage


def emptypage(wikidoc):
    text = wikidoc['revision']['text']
    if len(text)==0:
        return True
    elif len(text)==1 and not text[0]:
        return True
    else:
        return False
    

def filepage(wikidoc):
    """
    Check if page looks like a 'special' media / file page
    """
    otherwikis = ['wiktionary',
                  'wikiquote',
                  'wikisource',
                  'wikispecies',
                  'wikivoyage',
                  'betawikiversity',
                  'wikiversity',
                  'wikimedia',
                  'wikibooks',
                  'wmf',
                  'commons',]
    otherwikis = [''.join([k,':']) for k in otherwikis]
    ignorelist = ['special:',
                  'media:',
                  'file:',
                  'template:',
                  'wikipedia:articles for deletion',
                  'portal:',
                  'category:',
                  'wikipedia:',
                  'image:',]
    ignorelist.extend(otherwikis)
    fileextlist = ['.jpg', '.gif', '.png', '.jpeg', ]
    title = wikidoc['title']
    for phrase in ignorelist:
        if title.lower().startswith(phrase):
            return True
    for phrase in fileextlist:
        if title.lower().endswith(phrase):
            return True
    return False



######################################################################
#{ Example usage
######################################################################


if __name__=="__main__":
    wi = WikiPageIterator()
    for doc in wi:
        print(doc['title'])
