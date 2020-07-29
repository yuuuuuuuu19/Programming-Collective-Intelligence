import feedparser
import re


def read(feed, classifier):
    f = feedparser.parse(feed)

    for entry in f['entries']:
        print()
        print('-----')
        print(f'Title: {entry["title"].encode("utf-8")}')
        print(f'Publisher: {entry["publisher"].encode("utf-8")}')
        print()
        print(f'Summary:\n{entry["summary"].encode("utf-8")}')

        # combine all the text and pass to classifier
        full_txt = f'{entry["title"]}\n{entry["publisher"]}\n{entry["summary"]}'
        print(f'Guess: {classifier.classify(full_txt)}')

        cl = input('Enter category: ')
        classifier.train(full_txt, cl)


def entry_features(entry):
    splitter = re.compile(r'\W+')
    f = {}

    title_words = [s.lower() for s in splitter.split(entry["title"]) if 2 < len(s) < 20]
    for w in title_words:
        f['Title:' + w] += 1

    summary_words = [s for s in splitter.split(entry["summary"]) if 2 < len(s) < 20]

    # upper case count
    uc = 0
    for i in range(len(summary_words)):
        w = summary_words[i]
        f[w.lower()] = 1
        uc += w.isupper()

        if i < len(summary_words) - 1:
            word_pair = ' '.join(summary_words[i:i + 2])
            f[word_pair.lower()] += 1

    f['Publisher:' + entry['publisher']] = 1

    if uc/len(summary_words) > 0.3:
        f['UPPERCASE'] = 1

    return f