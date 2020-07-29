from chap10 import news_corpas
from chap6 import classifier
import random

def test():
    all_words, article_words, article_title = news_corpas.get_article_words()
    matrix, word_vector = news_corpas.make_matrix(all_words, article_title, all_words)

    for i in matrix:
        print(sum(i))


def test2():
    all_words, article_words, article_title = news_corpas.get_article_words()
    matrix, word_vector = news_corpas.make_matrix(all_words, article_title, all_words)

    def features(x):
        return [j for i, j in zip(x, word_vector) if i > 0]

    cl = classifier.NaiveBayes(features, db_name='news_feed')


test()
