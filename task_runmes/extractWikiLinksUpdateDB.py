
import sys
import time

sys.path.append('/Users/immersinn/Gits/')
from wikipedia_processing.wikiprep.wikiMDBPageIterator \
     import WikiPageIterator, getWikiMDBConn
from wikipedia_processing.wikiprep.basicLinkExt \
     import extractWikiLinksFromDoc


def createDocToFromList(doc_name, doc_links, linkFilter):
    """

    """
    to_from_info = []
    for section_name,section_links in doc_links.items():
        from_page = {'article':doc_name,
                     'section':section_name}
        links = linkFilter(section_links)
        for link in links:
            to_from_info.append({'from_page':from_page,
                                 'to_page':link['link'],
                                 'text':link['text'],
                                 'lType':link['lType']})
    return to_from_info


def main(max_pages):
    print("Making connection to Mongo Wiki DB...")
    wikiMDBCon = getWikiMDBConn()
    print("Iterating over documents for analysis...")
    wi = WikiPageIterator(limit=max_pages)
    count = 0
    for doc in wi:
        if count%1000==0:
            title = doc['title']
            print("At %s, doc number %s" % (title, count))
        count += 1
        doc_id = doc['_id']
        output = extractWikiLinksFromDoc(doc)
        doc_to_from = createDocToFromList(doc['title'],
                                          output['links'],
                                          lambda x: filter(None, x))
        doc_to_from = {i:j for i,j in enumerate(doc_to_from)}
        # mycollection.update({'_id':mongo_id},
        #                     {"$set": post},
        #                     upsert=False)
##        wikiMDBCon.coll.update({'_id':doc_id},
##                               {"$set": \
##                                {'to_from_wikiLinks':doc_to_from}})
        

if __name__=="__main__":
    limit = 0
    main(limit)
