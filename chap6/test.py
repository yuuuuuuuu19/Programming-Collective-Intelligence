from chap6 import classifier, doc_class, feed_filter

def test1():
    cl = classifier.Classifier(doc_class.get_words)
    doc_class.sample_train(cl)
    word = 'quick'
    cg = cl.fcount(word, 'good')
    cb = cl.fcount(word, 'bad')
    pr = cl.fprob(word, 'good')
    pr_ = cl.weighted_prob('money', 'good', cl.fprob)
    print(f'word => {word}\n\tgood:{cg}\n\t bad:{cb}\n\tprobability {pr}')
    doc_class.sample_train(cl)
    print(pr_)

def test2():
    cl = classifier.NaiveBayes(doc_class.get_words)
    #doc_class.sample_train(cl_v)
    #pr_v = cl_v.prob('quick rabbit', 'good')
    #pr_v_ = cl_v.prob('quick rabbit', 'bad')
    #print(pr_v)
    #print(pr_v_)

    cl.classify('quick money', default='unknown')
    doc_class.sample_train(cl)
    print(cl.classify('quick rabbit', default='unknown'))
    print(cl.classify('quick money', default='unknown'))
    cl.set_threshold('bad', 3)
    print(cl.classify('quick money', default='unknown'))
    for _ in range(10):
        doc_class.sample_train(cl)
    print(cl.classify('quick money', default='unknown'))

    print(cl.__getattribute__('thresholds'))
    cl.classify('quick money', default='unknown')

def test3():
    cl = classifier.FisherClassifier(doc_class.get_words, db_name='test.db')
    doc_class.sample_train(cl)
    print(cl.cprob('quick', 'good'))
    print(cl.cprob('money', 'bad'))
    print(cl.weighted_prob('money', 'bad', cl.cprob))
    print(cl.fisher_prob('quick rabbit', 'good'))
    print(cl.fisher_prob('quick rabbit', 'bad'))

    print()

    print(cl.classity('quick rabbit'))
    print(cl.classity('quick money'))

    cl.set_minimumus('bad', 0.8)
    print(cl.classity('quick money'))

    cl.set_minimumus('good', 0.4)
    print(cl.classity('quick money'))

def test4():
    cl = classifier.FisherClassifier(doc_class.get_words, 'test1.db')
    doc_class.sample_train(cl)

    cl2 = classifier.NaiveBayes(doc_class.get_words, 'test1.db')
    print(cl2.classify('quick money'))


def test5():
    cl = classifier.FisherClassifier(doc_class.get_words, 'test.db')
    feed_filter.read('python_search.xml', cl)


def test6():
    cl = classifier.FisherClassifier(feed_filter.entry_features, 'python_feed.db')
    feed_filter.read('python_search.xml', cl)





#test1()
#test2()
#test3()
#test4()
test5()