from functools import lru_cache
import requests
import math
import sys
import random

sys.setrecursionlimit(100000)


def readfile(url):
    response = requests.get(url)

    data = []
    for s in response.text.split('\r\n'):
        if len(s) > 0:
            data.append(s.split('\t'))

    cols = tuple(data[0])
    *trans, = zip(*data[1:])
    rows = trans[0]
    *data_str, = zip(*trans[1:])
    table = tuple(tuple(map(lambda x: int(x), i)) for i in data_str)

    return {"cols": cols, "rows": rows, "table": table}


@lru_cache(maxsize=100000)
def distance_peason(x, y):
    n = len(x)
    if n == 0:
        return 0
    _x = sum(x) / n
    _y = sum(y) / n
    s_xy = sum((i - _x) * (j - _y) for i, j in zip(x, y))
    s_x = math.sqrt(sum((i - _x) ** 2 for i in x))
    s_y = math.sqrt(sum((i - _y) ** 2 for i in y))
    if s_x * s_y == 0:
        return 0

    r_xy = s_xy / (s_x * s_y)
    return 1 - r_xy


class Bicluster:
    def __init__(self, vec, left=None, right=None, dist=0.0, id=None):
        self.vec = vec
        self.left = left
        self.right = right
        self.dist = dist
        self.id = id


def print_node(clust, labels, depth=0):
    left = clust.left
    right = clust.right
    id = clust.id

    label = labels[id] if (left, right) == (None, None) else labels[id] + '>'

    print(' ' * depth + label)
    depth += 1
    if left is not None:
        print_node(left, labels, depth)
    if right is not None:
        print_node(right, labels, depth)


def hcluster(rows, dist_func=distance_peason):
    n = len(rows)
    clusts = [Bicluster(rows[i], id=i) for i in range(n)]
    merged = set()
    c = 0
    while c < n - 1:
        lowestpair = (-1, -1)
        dist_min = float("Inf")
        # find closest pair
        for i in range(n + c):
            clust1 = clusts[i]
            id1 = clust1.id
            vec1 = clust1.vec
            if id1 in merged:
                continue
            for j in range(i + 1, n + c):
                clust2 = clusts[j]
                id2 = clust2.id
                vec2 = clust2.vec
                if id2 in merged:
                    continue
                if id1 > id2:
                    id1, id2 = id2, id1

                d = dist_func(vec1, vec2)

                if d < dist_min:
                    dist_min = d
                    lowestpair = (id1, id2)

        # caliculate mean of closest pair
        id1, id2 = lowestpair
        vec_mergeed = tuple([(i + j) / 2 for i, j in zip(clusts[id1].vec, clusts[id2].vec)])
        merged |= {id1, id2}

        # create new cluster
        new_clust = Bicluster(vec_mergeed, left=clusts[id1], right=clusts[id2], dist=dist_min, id=n + c)
        clusts.append(new_clust)
        c += 1

    return clusts


def transpose_matrix(data):
    trans = [tuple(i) for i in zip(*data)]
    return trans


def k_means_clustering(rows, dist_func=distance_peason, k=4, max_iterations=100):
    dim = len(rows[0])
    ranges = [(min(i), max(i)) for i in zip(*rows)]
    # initialize centroid
    centroids = [tuple([random.randrange(r[0], r[1], 1) for r in ranges]) for _ in range(k)]

    last_matches = None

    for _ in range(max_iterations):
        matches = [[] for _ in range(k)]
        for i, row in enumerate(rows):
            num_cent = 0
            dist = float("Inf")
            for j, centroid in enumerate(centroids):
                dist_ij = dist_func(centroid, row)
                if dist_ij < dist:
                    dist = dist_ij
                    num_cent = j

            matches[num_cent].append(i)

        if last_matches == matches:
            break

        last_matches = matches
        # update centroids
        for i in range(k):
            group = [rows[j] for j in matches[i]]
            n = len(group)

            if n == 0:
                centroid = tuple([0] * dim)
            else:
                centroid = tuple([sum(j) / n for j in zip(*group)])

            centroids[i] = centroid

    return last_matches


def scale_down(data, dist_func=distance_peason, rate=0.01, max_iteration=1000):
    n = len(data)

    dist_real = [[dist_func(data[i], data[j]) for i in range(n)] for j in range(n)]

    outer_sum = 0

    # random initialization of staring points
    loc = [[random.random(), random.random()] for _ in range(n)]
    dist_fake = [[0] * n for _ in range(n)]

    last_error = None
    for m in range(max_iteration):
        for i in range(n):
            for j in range(n):
                dist_fake[i][j] = math.sqrt(sum((loc[i][x] - loc[j][x]) ** 2 for x in range(2)))

        grad = [[0, 0] for _ in range(n)]
        total_error = 0
        for k in range(n):
            for j in range(n):
                if j == k:
                    continue
                error_term = (dist_fake[j][k] - dist_real[j][k]) / dist_real[j][k]

                grad[k][0] += ((loc[k][0] - loc[j][0]) / dist_fake[j][k]) * error_term
                grad[k][1] += ((loc[k][1] - loc[j][1]) / dist_fake[j][k]) * error_term

                total_error += abs(error_term)

        print(f'{m} total error: {total_error}')

        if last_error and total_error > last_error:
            break
        last_error = total_error

        for k in range(n):
            loc[k][0] -= rate * grad[k][0]
            loc[k][1] -= rate * grad[k][1]

    return loc

