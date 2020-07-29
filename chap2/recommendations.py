# 2020-07-22
# Python3

import math
from collections import defaultdict
import urllib.request
import io
import zipfile
import re

# user's critics
reviews = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Returns': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Returns': 5.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5,
        'The Night Listener': 4.0
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'The Night Listener': 4.5,
        'Superman Returns': 4.0,
        'You, Me and Dupree': 2.5
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Returns': 3.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0,
        'Superman Returns': 5.0,
        'You, Me and Dupree': 3.5
    },
    'Toby': {
        'Snakes on a Plane': 4.5,
        'You, Me and Dupree': 1.0,
        'Superman Returns': 4.0
    }
}


# define similarity score by Euclidean distance
def sim_score_eucrid(reviews, p1, p2):
    # common evaluation item
    rev1 = reviews[p1]
    rev2 = reviews[p2]
    si = list(set(rev1.keys()) & set(rev2.keys()))

    distance = math.sqrt(sum((rev1[item] - rev2[item]) ** 2 for item in si))
    score = 1 / (1 + distance)
    return score


# define similarity score by Pearson correlation coefficient
def sim_score_peason(reviews, p1, p2):
    # common evaluation item
    rev1 = reviews[p1]
    rev2 = reviews[p2]
    si = list(set(rev1.keys()) & set(rev2.keys()))

    n = len(si)
    if n == 0:
        return 0

    x = sum(rev1[item] for item in si) / n
    y = sum(rev2[item] for item in si) / n
    s_xy = sum((rev1[item] - x) * (rev2[item] - y) for item in si)
    s_x = math.sqrt(sum((rev1[item] - x) ** 2 for item in si))
    s_y = math.sqrt(sum((rev2[item] - y) ** 2 for item in si))
    if s_x * s_y == 0:
        return 0

    r_xy = s_xy / (s_x * s_y)
    return r_xy


# return best matching n people
def top_matches(reviews, person, n=5, func=sim_score_peason):
    res = []
    for other in reviews.keys():
        if other == person:
            continue
        sim = func(reviews, person, other)
        res.append((other, sim))
    res.sort(key=lambda arr: arr[1], reverse=True)
    return res[:n]


# define recommendation function
def get_recommendations(reviews, person, func=sim_score_peason):
    watched = reviews[person]
    candidate = defaultdict(lambda: defaultdict(int))

    for other in reviews.keys():
        if other == person:
            continue
        sim = func(reviews, person, other)

        if sim <= 0:
            continue

        for title, point in reviews[other].items():
            if title not in watched:
                candidate[title]["score"] += sim * point
                candidate[title]["similarity"] += sim

    rankings = [(title, value["score"] / value["similarity"]) for title, value in candidate.items()]
    rankings.sort(key=lambda arr: arr[1], reverse=True)

    return rankings


# define function returns item review
def transform_review(reviews):
    # person : title : review point <=> title : person : review point
    res = defaultdict(dict)
    for person, dic in reviews.items():
        for title, point in dic.items():
            res[title][person] = point

    return res


def calc_similar_items(reviews, func=sim_score_eucrid):
    res = {}
    items = transform_review(reviews)
    num = len(items)
    count = 0
    for item in items:
        count += 1
        if count % 100 == 0:
            print(f"{count} / {num}")
        # find similar items
        scores = top_matches(items, item, func=func)
        res[item] = scores

    return res


def get_recommended_items(reviews, user):
    items_similarity = calc_similar_items(reviews, func=sim_score_eucrid)
    ratings = reviews[user]
    rated = ratings.keys()
    items = defaultdict(lambda: defaultdict(int))
    for item, rating in ratings.items():
        for item2, similarity in items_similarity[item]:
            if item2 in rated:
                continue

            items[item2]["score"] += similarity * rating
            items[item2]["total"] += similarity

    # normalization
    rankings = [(item, items[item]["score"] / items[item]["total"]) for item in items.keys()]

    rankings.sort(key=lambda arr: arr[1], reverse=True)

    return rankings


def load_movielens():
    url = "http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
    response = urllib.request.urlopen(url)
    with zipfile.ZipFile(io.BytesIO(response.read())) as bs:
        movies_csv = bs.read('ml-latest-small/movies.csv').decode()
        reviews_csv = bs.read('ml-latest-small/ratings.csv').decode()

        movies = {}
        reviews = defaultdict(dict)
        pattern = r'(\d+),\"?([a-zA-Z0-9\'!\/\?:\s\.\-\(\)\&,:]+)\"?,?\((\d{4})\),([a-zA-Z|]+)'
        pattern2 = r'(\d+),[\"\']{1}([a-zA-Z0-9\'!\/\?:\s\.\-\(\)\&,:]+),([a-zA-Z\s]+)?\(([0-9]+)\)[\'\"]{1}?,([a-zA-Z|]+)'

        for i in movies_csv.split('\n'):
            mtc = re.match(pattern, i)
            if mtc is not None:
                grp = mtc.groups()
                id = grp[0]
                title = grp[1][:-1]
                year = grp[2]
                genre = grp[3].split('|')
                movies[id] = title
            else:
                mtc = re.match(pattern2, i)
                if mtc is not None:
                    grp = mtc.groups()
                    id = grp[0]
                    title = grp[1]
                    year = grp[3]
                    genre = grp[-1].split('|')
                    movies[id] = title

        for i in reviews_csv.split('\r\n')[4:]:
            review = i.split(',')
            if len(review) != 4:
                continue
            user_id = review[0]
            movie_id = review[1]
            rating = float(review[2])
            if movie_id in movies.keys():
                reviews[user_id][movie_id] = rating

        return [movies, reviews]