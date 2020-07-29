from chap9 import match
import math


def liner_train(rows):
    avgs = {}
    cnts = {}

    for row in rows:
        cl = row.match
        avgs.setdefault(cl, [0, 0] * len(row.data))
        cnts.setdefault(cl, 0)

        for i in range(len(row.data)):
            avgs[cl][i] += row.data[i]

        cnts[cl] += 1

    for cl, avg in avgs.items():
        for i in range(len(avg)):
            avg[i] /= cnts[cl]

    return avgs


def dot_product(v1, v2):
    return sum(i * j for i, j in zip(v1, v2))


def dp_classify(point, avgs):
    b = dot_product(avgs[1], avgs[1]) - dot_product(avgs[0], avgs[0])
    b /= 2
    y = dot_product(point, avgs[0]) - dot_product(point, avgs[1]) + b
    if y > 0:
        return 0
    else:
        return 1


def yes_no(v):
    d = {'yes': 1, 'no': -1}
    a = d.get(v)
    if a is None:
        return 0
    return a


def match_count(i1, i2):
    l1 = set(i1.split(':'))
    l2 = set(i2.split(':'))
    l3 = l1 & l2
    return len(l3)


def scale_data(rows):
    low = [10 ** 9] * len(rows[0].data)
    high = [10 ** 9] * len(rows[0].data)

    for row in rows:
        d = row.data
        for i in range(len(d)):
            if d[i] < low[i]:
                low[i] = d[i]
            if d[i] > high[i]:
                high[i] = d[i]

        def scale_input(d):
            return [(d.data - low[i]) / (high[i] - low[i]) for i in range(len(row))]

        newrows = [match.Match(scale_input(row.data) + [row.match]) for row in rows]

        return newrows, scale_input


def rbf(v1, v2, gamma=20):
    d = sum(pow(i - j, 2) for i, j in zip(v1, v2))
    return math.exp(-gamma * d)


def n_classify(point, rows, offset, gamma=10):
    s0 = 0
    s1 = 0
    c0 = 0
    c1 = 0

    for row in rows:
        if row.match == 0:
            s0 += rbf(point, row.data, gamma)
            c0 += 1
        else:
            s1 += rbf(point, row.data, gamma)
            c1 += 1
    y = 1 / c0 * s0 - 1 / c1 * s1 + offset
    if y > 0:
        return 0
    else:
        return 1


def get_offest(rows, gamma=10):
    l0=[]
    l1 = []
    for row in rows:
        if row.match == 0:
            l0.append(row.data)
        else:
            l1.append(row.data)
    s0 = sum(sum(rbf(v1, v2, gamma) for v1 in l0) for v2 in l0)
    s1 = sum(sum(rbf(v1, v2, gamma) for v0 in l1) for v2 in l1)

    offset = 1/len(l1) ** 2 * s1 - 1/len(l0) ** 2
    offset *= s0

    return offset


