
import sys
from sys import getsizeof
import re
import bson
from bson.binary import (OLD_UUID_SUBTYPE, UUID_SUBTYPE,
                         JAVA_LEGACY, CSHARP_LEGACY)


class populateWikiMDB():
    """
    #0: find where the first page begins and set cursor there
    #1: parseWikiXML is called
    """

    def __init__(self, mdb_obj, file_path, max_count=-1):
        self.mdb_obj = mdb_obj
        self.fn = file_path
        self.verbose = False
        self.createFileHandle()
        self.findFirstPage()
        self.eof = False
        self.current_page = []
        self.max_count = max_count
        self.mainProcess()


    def createFileHandle(self):
        try:
            self.wiki_file = open(self.fn, 'r')
        except IOError:
            print("Invalid file name provided.")
            sys.exit(0)


    def findFirstPage(self):
        stop = False
        count = 0
        while not stop:
            current_line = self.wiki_file.readline()
            if current_line.strip()=='<page>':
                stop = True
            else:
                count += 1
        self.wiki_file.close()
        self.createFileHandle()
        for i in range(count):
            line = self.wiki_file.readline()


    def mainProcess(self):
        self.count = 0
        while not self.eof and self.count != self.max_count:
            self.getPage()
            if self.current_page:
                if self.count % 10000 == 0:
                    print(self.current_page[0])
                self.parsePage()
                self.insertPage()
            self.count += 1


    def getPage(self):
        """
        Finds each subsequent page
        """
        end = False
        page = []
        save_line = False
        while not end:
            current_line = self.wiki_file.readline()
            if current_line.strip()=='<page>':
                save_line = True
            elif not current_line:
                end = True
                self.eof = True
            elif save_line:
                if current_line.strip()=='</page>':
                    end = True
                else:
                    page.append(current_line)
        self.current_page = page


    def parsePage(self):
        self.current_page = [p.strip() for p in self.current_page]
        self.current_page = parsePageXML(self.current_page)
        self.encodePageTest()


    def encodePageTest(self):
        self.encoded = bson.BSON.encode({'text':self.current_page['dict']['revision']['text']},
                                           True)
        #, UUID_SUBTYPE
        self.encoded_length = len(self.encoded)
        if self.verbose:
            print('Size of text: %s' % self.encoded_length)


    def insertPage(self):
        if self.encoded_length > 13000000:
            print('Splitting text into sections...')
            self.splitParsedPageXML()
            for p in self.current_page:
                ids = self.mdb_obj.insert(p, return_ids=True)
                
        else:
            ids = self.mdb_obj.insert(self.current_page, return_ids=True)
    

    def splitParsedPageXML(self):
        """
        Takes a parsed page dictionary, and divides it into several pieces.
        Specifically, all page "meta data" (read: non-text data) is placed
        in a single dictionary to be written to MDB, while the textual part
        of the page is split into paragraphs
        """
        section_re_match = re.compile(r'^==(?!=)(.+)==$')
        text = self.current_page['revision']['text']
        title = self.current_page['title']
        _id = self.current_page['id']
        parsed_page_list = [self.current_page]
        curcont = []
        header = 'FrontMatter'
        for t in text:
            mat = re.match(section_re_match, t)
            if mat:
                parsed_page_list.append({'title':title, 'id':_id,
                                       'header':header,
                                       'content':curcont})
                header = mat.groups()[0]
                curcont = []
            else:
                curcont.append(t)
        parsed_page_list.append({'title':title, 'id':_id,
                                 'header':header,
                                 'content':curcont})
        total_sections = len(parsed_page_list)
        print('Total number of sections for %s: %s' % (title, total_sections))
        self.current_page = parsed_page_list


def parsePageXML(pagexml, index=0, closing=None):
    """
    Keep it simple: turn the XML into a dictionary structure
    """
    new_dict = {}
    content = []
    while index<len(pagexml):
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
    return {'dict':new_dict,
            'content':content,
            'index':index+1}
