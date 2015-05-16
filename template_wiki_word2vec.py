
import re
import nltk
from gensim.models import Word2Vec

from bs4 import BeautifulSoup
from nltk.corpus import stopwords

from wikipedia_processing.wikiMDBPageIterator import WikiPageIterator


class WikiIterParse(WikiPageIterator):

    def __init__(self, docOrPage):
        pass


    def next(self):
        pass




class WikiDocParseUtility(object):
    """

    """

    @staticmethod
    def clean_wiki_doc(article_dict, return_all=False):
        try:
            article = article_dict['revision']['text']
        except KeyError:
            pass

        if return_all:
            article['cleand_text'] = cleaned_article_text
            return article
        else:
            return cleaned_article_text


    @staticmethod
    def article_to_wordlist(article, remove_stopwords=False):

        # 1 Pre-processing

        # 2 Convert words to lower case and split them

        # 3 Optionally remove stop words (false by default)
        
        return words


    @staticmethod
    def article_to_sentences(article, tokenizer, remove_stopwords=False):

        # 1. Use the NLTK tokenizer to split the paragraph into sentences
        raw_sentences = tokenizer.tokenize(review.decode('utf8').strip())

        # 2. Loop over each sentence
        sentences = []
        for raw_sentence in raw_sentences:
            # If a sentence is empty, skip it
            if len(raw_sentence) > 0:
                # Otherwise, call review_to_wordlist to get a list of words
                sentences.append(WikiDocParse.review_to_wordlist( raw_sentence, \
                  remove_stopwords ))
        
        return sentences
