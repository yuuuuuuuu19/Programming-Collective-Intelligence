import math
import random


def euclidean(v1, v2):
    return math.sqrt(sum(pow(i - j, 2) for i, j in zip(v1, v2)))


def get_distance(data, vec):
    n = len(data)
    distances = []
    for i, d in enumerate(data):
        inp = d['input']
        distances.append((i, euclidean(vec, inp)))
    distances.sort(key=lambda x: x[1])
    return distances


def inverse_weight(dist, num=1, const=0.1):
    return num / (dist + const)


def subtract_weight(dist, const=1):
    return max(0, const - dist)


def gaussian(dist, sigma=10):
    return pow(math.e, -1 / 2 * pow(dist / sigma, 2))


def divide_data(data, test_ratio=0.5):
    train_data = []
    test_data = []
    for row in data:
        if random.random() < test_ratio:
            test_data.append(row)
        else:
            train_data.append(row)

    return (train_data, test_data)


def rescale(data, scale):
    scaled_data = []
    for row in data:
        scaled = [i * j for i, j in zip(scale, row['input'])]
        scaled_data.append({'input': scaled, 'result': row['result']})
    return scaled_data


def knn_estimate(data, vec, k=5):
    # get sorted distance list
    dist = get_distance(data, vec)
    sum_k = 0
    # average of nearest k items
    for i, _ in dist[:k]:
        sum_k += data[i]['result']

    avg = sum_k / k
    return avg


def weighted_knn(data, vec, k=5, weight_func=gaussian):
    distances = get_distance(data, vec)
    sum_k = 0
    total_weight = 0.0001
    for item in distances[:k]:
        id = item[0]
        dist = item[1]
        weight = weight_func(dist)
        total_weight += weight
        sum_k += weight * data[id]['result']

    avg = sum_k / total_weight
    return avg


def test_algorithm(alg, train_data, test_data, k=5):
    error = 0
    for row in test_data:
        guess = alg(train_data, row['input'], k=k)
        error += pow(row['result'] - guess, 2)

    return error / len(test_data)


def cross_validation(alg, data, trials=100, test_ratio=0.5, k=5):
    error = 0

    for i in range(trials):
        train_data, test_data = divide_data(data, test_ratio)
        error += test_algorithm(alg, train_data, test_data, k=k)

    error_avg = error / trials
    return error_avg


def create_cost_func(alg, data):
    def costf(scale):
        scaled_data = rescale(data, scale)
        return cross_validation(alg, scaled_data, trials=10)

    return costf


def prob_guess(data, vec, low, high, k=5, weightf=gaussian):
    dist = get_distance(data, vec)
    nweight = 0
    tweight = 0

    for i in range(k):
        idx = dist[i][0]
        d = dist[i][1]
        weight = weightf(d)
        v = data[idx]['result']

        if low <= v <= high:
            nweight += weight
        tweight += weight
    if tweight == 0:
        return 0
    return nweight / tweight
