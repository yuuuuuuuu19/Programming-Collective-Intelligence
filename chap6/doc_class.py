from chap6 import classifier
import re
import math

def get_words(doc):
    splitter = re.compile(r'\W+')
    words = [s.lower() for s in splitter.split(doc) if 2 < len(s) < 20]
    return dict([(w,1) for w in words])

def sample_train(cl):
    train_data = {'good':['Nobody owns the water',
                           'the quick rabbit jumps fences',
                           'the quick brown fox jumps'],
                   'bad':['buy pharmaceuticals now',
                          'make quick money at the online casino']}

    for cat, samples in train_data.items():
        for sample in samples:
            cl.train(sample, cat)
