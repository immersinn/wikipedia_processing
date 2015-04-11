import wikiMDBPageIterator
import wikiparsemarkup


def main():
    '''Get list of wiki docs, texts'''
    pi = wikiMDBPageIterator.WikiPageIterator(limit=300)
    docs = []
    for d in pi:
        docs.append(d)
    docs = filter(notextfilter, docs) # each line is a piece of content...
    texts = [wikiparsemarkup.preprocessWikiDoc(doc) for doc in docs]
    titles = [d['title'] for d in docs]
    newdocs = [{'title':t,
                'text':mergedocparts(x)} for (t,x) in zip(titles, texts)]
    return newdocs



def notextfilter(doc):
    if not doc['revision']['text']:
        return False
    else:
        return True


def mergedocparts(doc):
    """Merges word lists into paragraphs, and paragraphs into a doc"""
    doc = [' '.join(p) for p in doc]
    doc = '\n'.join(doc)
    return doc
