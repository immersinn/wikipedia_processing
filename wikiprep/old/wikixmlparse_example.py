from sys import getsizeof
import re


import bson
from bson.binary import (OLD_UUID_SUBTYPE, UUID_SUBTYPE,
                         JAVA_LEGACY, CSHARP_LEGACY)


class unpackWikiArticles():

    def __init__(self, file_name='',):
        file_name = file_name if file_name \
                    else '/Users/immersinn/Documents/enwiki-latest-pages-articles.xml'
        self.fn = file_name


    def createFileHandle(self):
        try:
            wiki_file = open(self.fn)
            self.wiki_file = wiki_file
        except IOError:
            print("Invalid file name provided.")


def findFirstPage():
    fh = createFileHandle()
    stop = False
    count = 0
    while not stop:
        current_line = fh.readline()
        if current_line.strip()=='<page>':
            stop = True
        else:
            count += 1
    fh.close()
    fh = createFileHandle()
    for i in range(count):
        line = fh.readline()
    return fh


def getPage(wikifilehandle):
    """
    Finds each subsequent page
    """
    eof=False
    end = False
    page = []
    save_line = False
    while not end:
        current_line = wikifilehandle.readline()
        if current_line.strip()=='<page>':
            save_line = True
        elif not current_line:
            end=True
            eof=True
        elif save_line:
            if current_line.strip()=='</page>':
                end=True
            else:
                page.append(current_line)
    return {'page':page,
            'fh':wikifilehandle,
            'eof':eof,}
    

def parseWikiXML(fh, mdbObj):
    stop = False
    total_size = 0
    while not stop:
        pageInfo = getPage(fh)
        if pageInfo['eof']:
            stop=True
        else:
            fh = pageInfo['fh']
        if pageInfo['page']:
            page = pageInfo['page']
            page = [p.strip() for p in page]
            parsedPage = parsePageXML(page)['dict']

##            encoded = bson.BSON.encode(parsedPage, True, UUID_SUBTYPE)
##            encoded_length = len(encoded)
##            print('Size of insert: %s' % encoded_length)

            encoded = bson.BSON.encode({'text':parsedPage['revision']['text']},
                                       True, UUID_SUBTYPE)
            encoded_length = len(encoded)
            print('Size of text: %s' % encoded_length)

            if encoded_length > 13000000:
                print('Splitting text into sections...')
                parsedPageList = splitParsedPageXML(parsedPage)
                for p in parsedPageList:
                    ids = mdbObj.MongoInsert(p,
                                             return_ids=True)
                    
            else:
                ids = mdbObj.MongoInsert(parsedPage,
                                         return_ids=True)
                
                
##            print ids

            
def parsePageXML(pagexml, index=0, closing=None):
    """
    Keep it simple: turn the XML into a dictionary structure
    """
    new_dict = {}
    content = []
    while index<len(pagexml):
##        print('current line: %s' % pagexml[index])
        match = re.match('^<([a-z0-9]+).*>', pagexml[index])
        if match:
            target = match.groups()[0]
            if re.search('/>$', pagexml[index]):
                match = re.match('^<'+target+'(.*)/>$', pagexml[index])
                new_dict[target] = match.groups()[0]
                index += 1
            elif re.search(r'</' + target + '>$', pagexml[index]):
                match = re.match('^<'+target+'.*>(.*)</'+target+'>$',
                                   pagexml[index])
                new_dict[target] = match.groups()[0]
                index += 1
            else:
                data = parsePageXML(pagexml,
                                    index=index+1,
                                    closing=target,)
                if 'dict' in data.keys() and data['dict']:
                    new_dict[target] = data['dict']
                else:
                    new_dict[target] = data['content']
                index = data['index']
        elif re.search(r'</' + closing + '>$', pagexml[index]):
            return {'dict':new_dict,
                    'content':content,
                    'index':index+1}
        else:
            content.append(pagexml[index])
            index += 1
##        print('current dict: %s' % new_dict)
##        print('current content: %s' % content)
##        print('current closure: %s' % closing)
    return {'dict':new_dict,
            'content':content,
            'index':index+1}


def splitParsedPageXML(parsedpage):
    """
    Takes a parsed page dictionary, and divides it into several pieces.
    Specifically, all page "meta data" (read: non-text data) is placed
    in a single dictionary to be written to MDB, while the textual part
    of the page is split into paragraphs
    """
    sectionReMatch = re.compile(r'^==(?!=)(.+)==$')
    text = parsedpage['revision']['text']
    title = parsedpage['title']
    _id = parsedpage['id']
    parsedPageList = [parsedpage]
    curcont = []
    header = 'FrontMatter'
    for t in text:
        mat = re.match(sectionReMatch, t)
        if mat:
            parsedPageList.append({'title':title, 'id':_id,
                                   'header':header,
                                   'content':curcont})
            header = mat.groups()[0]
            curcont = []
        else:
            curcont.append(t)
    parsedPageList.append({'title':title, 'id':_id,
                           'header':header,
                           'content':curcont})
    total_sections = len(parsedPageList)
    print('Total number of sections for %s: %s' % (title, total_sections))
    return parsedPageList
    
