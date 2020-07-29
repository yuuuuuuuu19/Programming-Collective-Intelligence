import re
import feedparser
import urllib.request

# some news feed url offered by text book is broken
# or redirects to new web page
feed_list = [
    'http://feeds.washingtonpost.com/rss/rss_powerpost?itid=lk_inline_manual_4',
    'http://feeds.washingtonpost.com/rss/rss_innovations?itid=lk_inline_manual_41',
    'https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss',
    'https://www.wired.com/feed',
    'https://www.macworld.com/index.rss',
    'https://www.pcworld.com/index.rss',
    'https://feeds.npr.org/1019/rss.xml',
    'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml',
    'http://www.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml',
    'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
    'https://www.nba.com/jazz/rss.xml',
    'http://news.google.com/?output=rss',
    'http://www.salon.com/feed/',
    'https://www2.smartbrief.com/servlet/rss?b=ASCD',
    'https://www.ed.gov/feed'
    ]


def split_HTML(html):
    pattern = re.compile(r'>([^><]+)<')
    match = pattern.findall(html)
    res = ' '.join(match)
    return res


def separate_words(text):
    pattern = re.compile(r'\W+')
    splitted = pattern.split(text)
    *filtered, = filter(lambda x: len(x) > 3, splitted)
    return filtered


def get_article_words():
    all_words = {}
    article_words = []
    article_titles = []
    entry_count = 0

    for feed in feed_list:
        print(f'parsing {feed} ...')

        f = feedparser.parse(feed)

        # loop all articles
        for e in f.entries:
            if e.title in article_titles:
                continue

            txt = e.title + split_HTML(e.description)
            words = separate_words(txt)
            article_words.append({})
            article_titles.append(e.title)

            for word in words:
                all_words.setdefault(word, 0)
                all_words[word] += 1
                article_words[entry_count].setdefault(word, 0)
                article_words[entry_count][word] += 1

            entry_count += 1

    return (all_words, article_words, article_titles)


def make_matrix(all_words, article_title, article_words):
    n = len(article_words)
    f = lambda k: 3 < all_words[k] < 0.6 * n
    *word_vector, = filter(f, all_words.keys())

    matrix = [[int(word in article) for word in word_vector] for article in article_words]

    return matrix, word_vector
