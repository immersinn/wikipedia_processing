
import sys
import time
import pickle

from wikipedia_processing.wikiMDBPageIterator import WikiPageIterator, getWikiMDBConn
##from wikipedia_processing.basicLinkExt import extractWikiLinksFromDoc

from wikipedia_processing import basicLinkExt

sys.path.append('/home/immersinn/gdrive/Analytics/wiki_analytics/comparitive_clustering/python_code')
import wikiWord2VecUtil



##pkl_file_name = \
##              '/Users/immersinn/Gits/wikipedia_processing/task_runmes/extractWikiLinksUpdateDB_errors.pkl'
##pkl_file_name = \
##	      '/srv/logs/extractWikiLinksUpdateDB_errors.pkl'
pkl_file_name = \
              '/home/immersinn/Data/logs/extractWikiLinksUpdateDB_errors.pkl'


def createDocToFromList(doc_name, doc_links, linkFilter):
    """

    """
    to_from_info = []
    for section_name, section_links in doc_links.items():
        from_page = {'article':doc_name,
                     'section':section_name}
        links = linkFilter(section_links)
        for link in links:
            to_from_info.append({'from_page':from_page,
                                 'to_page':link['link'],
                                 'text':link['text'],
                                 'lType':link['lType']})

    for li in doc_links:
        from_page = {''}
    return to_from_info


def linksFromDoc(doc):
    '''
    '''
    article = wikiWord2VecUtil.extractWikiContent(doc['revision']['text'])
    article = wikiWord2VecUtil.removeRefs(article)
    article = wikiWord2VecUtil.simpleSectionSplit(article)
    output = basicLinkExt.extractWikiLinksFromDoc({'title' : doc['title'],
                                                    'content' : article})
    return(output)


def main(max_pages):
    try:
        errs = []
        print("Making connection to Mongo Wiki DB, link coll...")
        wikiLinkMDBCon = getWikiMDBConn(coll='wikiToWikiLinks')
        print("Iterating over documents for analysis...")
        wi = WikiPageIterator(limit=max_pages)
        count = 0
        for doc in wi:
            if count % 1000 == 0:
                title = doc['title']
                print("At %s, doc number %s" % (title, count))
            count += 1
            doc_id = doc['_id']
            try:
                output = linksFromDoc(doc)
                output['title'] = title
                doc_to_from = createDocToFromList(output['title'],
                                                  output['links'],
                                                  lambda x: filter(None, x))
                if doc_to_from:
                    wikiLinkMDBCon.insert(doc_to_from)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except:
                print('Error encounterd at document %s' % count)
                err_name = sys.exc_info()[1]
                print err_name
                new_error = {'mdb_id':doc['_id'],
                             'title':doc['title'],
                             'err_type':sys.exc_info()[0],
                             'err_msg':sys.exc_info()[1]}
                errs.append(new_error)
    finally:
        with open(pkl_file_name, 'w') as f1:
            pickle.dump(errs, f1)
        

if __name__=="__main__":
    limit = 0
    main(limit)
