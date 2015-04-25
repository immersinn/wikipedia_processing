
import sys
import networkx

sys.path.append('/Users/immersinn/Gits/')
import wikiMDBPageIterator


links_mdb = wikiMDBPageIterator.getWikiMDBConn(coll='wikiToWikiLinks')
links_graph = networkx.Graph()
links_mdb.query(limit = 1000000)

for doc in links_mdb.LastQ:
    links_graph.add_edge(doc['from_page']['article'],
                         doc['to_page']['article'])
