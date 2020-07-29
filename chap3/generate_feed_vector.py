import feedparser
import re
from collections import defaultdict
import requests


def get_words(html):
    pattern = re.compile(r'>([^<>\n]+?)<')
    match = pattern.findall(html)
    process = sum([re.split('\W+', i) for i in match], [])
    *result, = map(lambda x: x.lower(), process)
    *filtered, = filter(lambda x: len(x) > 0, result)

    return filtered


# return dict of RSS feed title and word frequency
def get_word_counts(url):
    # parse feed
    d = feedparser.parse(url)
    title = d.feed.title
    wc = defaultdict(int)

    # loop all entry
    for e in d["entries"]:
        summary = e.summary if "summary" in e else e.description

        # get word list
        words = get_words(e.title + summary)
        for word in words:
            wc[word] += 1

    wc_sorted = sorted(wc.items(), key=lambda x: x[1], reverse=True)
    return title, wc_sorted


def test():
    url = 'https://raw.githubusercontent.com/arthur-e/Programming-Collective-Intelligence/master/chapter3/feedlist.txt'

    response = requests.get(url)
    feedlist = response.text.split('\r\n')
    num = len(feedlist)
    wcs = defaultdict(int)
    apc = defaultdict(int)
    wli = []

    for i, feedurl in enumerate(feedlist):
        try:
            title, wc = get_word_counts(feedurl)
            wcs[title] = wc
            for (w, c) in wc:
                apc[w] += c
            print(f'{i}/{num} Success to parse feed: {feedurl}')
        except Exception as e:
            print(f'{i}/{num} Failed to parse feed: {feedurl}: {e}')

    for w, c in apc.items():
        if 0.1 < c / num < 0.5:
            wli.append(w)

    print(wli)
    for title, wc in wcs.items():
        res = []
        i = 0
        while i < min(50, len(wc)):
            w = wc[i][0]
            if w in wli:
                res.append(wc[i])
            i += 1

        print(res)

    print('Finish.')


test()
