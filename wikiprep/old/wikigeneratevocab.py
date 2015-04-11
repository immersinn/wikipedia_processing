from wikidocprocess import getProcessedDocText, getWikiMDBConn
from wikiMDBPageIterator import WikiPageIterator
from nltk import FreqDist
from NLP.nlp_extraction_tools import NLPPrepBasic



def generateVocabs():
    global_fd = FreqDist()
    global_doc_fd = FreqDist()
    realPages = WikiPageIterator()
    stop = False
    while not stop:
        try:
            doc = realPages.next()
            text = getProcessedDocText(doc)
            nlpobj = NLPPrepBasic(text)
            nlpobj.getWords()
            new_fd = FreqDist()
            global_fd.update(nlpobj.words)
            new_fd.update(nlpobj.words)
            global_doc_fd.update(new_fd.keys())
        except StopIteration:
            stop=True

    return {'wordFD':global_fd,
            'docFD':global_doc_fd}


def main():
    vocabdicts = generateVocabs()
    wikiword = getWikiMDBConn(coll='wordFD')
    wordFD = dict(vocabdicts['wordFD'])
    wikiword.MongoInsert({'words':wordFD.keys(),
                          'counts':wordFD.values()})
    wikiword.close()
    wikiword.makeCollConn('docFD')
    docFD = dict(vocabdicts['docFD'])
    wikiword.MongoInsert({'words':docFD.keys(),
                          'counts':docFD.values()})


if __name__=="__main__":
    main()
