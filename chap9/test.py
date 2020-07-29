from chap9 import match, advaned_classifier, yahoo_api
import matplotlib.pyplot as plt
import numpy as np


def test():
    agesonly = match.load_match('agesonly.csv')
    machmaker = match.load_match('matchmaker.csv')


def test2():
    agesonly = match.load_match('agesonly.csv')
    machmaker = match.load_match('matchmaker.csv')

    avgs = advaned_classifier.liner_train(agesonly)
    print(avgs)
    print(advaned_classifier.dp_classify([30, 30], avgs))
    print(advaned_classifier.dp_classify([25, 40], avgs))
    print(advaned_classifier.dp_classify([48, 20], avgs))

def test3():
    loc = yahoo_api.get_location('1 alewife center, cambridge, ma')
    print(loc)


test3()

def plot_age_matches(rows):
    xdm = [r.data[0] for r in rows if r.match == 1]
    ydm = [r.data[1] for r in rows if r.match == 1]
    xdn = [r.data[0] for r in rows if r.match == 0]
    ydn = [r.data[1] for r in rows if r.match == 0]

    f = plt.figure()
    plt.scatter(xdm, ydm, marker='o')
    plt.scatter(xdn, ydn, marker='x')
    plt.xlabel("age(M)")
    plt.ylabel("age(F)")
    plt.savefig('agesonly.png')
    plt.show()


test()
