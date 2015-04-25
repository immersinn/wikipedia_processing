#0 Create Wiki db in MongoDB
#1 Create article collection in the Wiki DB
#2 Read in the Wiki File
#3 Can I add some automated testing in here (e.g. query docs?)
#4 Can I add in a (optional) clean-up step?

import sys

sys.path.append('/Users/immersinn/Gits/')
from dbinterface_python.dbconns import connectMon
from wikipedia_processing.wikiprep.wikiXMLParse\
     import populateWikiMDB


default_wiki_xml_path = \'/Users/immersinn/Data/WebDataDumps/enwiki-latest-pages-articles.xml'

def createAndReturnWikiMDB():
    wikimdb = connectMon.MongoConn()
    print("Enter new DB name or hit return for default:")
    db_name = input()
    db_name = db_name if db_name else 'WikiData'
    print("Enter new collection name or hit return for default:")
    coll_name = input()
    coll_name = coll_name if coll_name else 'articleDump'
    wikimdb.makeDBConn(db_name)
    wikimdb.makeCollConn(coll_name)
    return wikimdb


def main():
    wikimdb_handle = createAndReturnWikiMDB()
    print('Enter path to WikiXML file:')
    file_path = input()
    file_path = file_path if file_path else default_wiki_xml_path
    populateWikiMDB(wikimdb_handle, file_path, max_count=1000)


if __name__=="__main__":
    main()
