from chap8 import wine_price, knn
from chap5 import optimization


def test():
    price = wine_price.wine_price(95, 3)
    print(price)

    samples = wine_price.wine_set1(sample_size=5)
    for sample in samples:
        rating = sample['input'][0]
        age = sample['input'][1]
        price = sample['result']
        print(f'rating: {rating} age: {age} price: {price}')


def test2():
    samples = wine_price.wine_set1(sample_size=300)
    max_k = 5
    for i in range(1, max_k + 1):
        error = knn.cross_validation(knn.weighted_knn, samples, trials=100, test_ratio=0.5, k=i)
        print(f'k:{i} error:{error}')


def test3():
    samples = wine_price.wine_set2(sample_size=300)

    rescale = knn.rescale(samples, [5, 5, 0, 1])
    max_k = 5
    for i in range(1, max_k + 1):
        error = knn.cross_validation(knn.weighted_knn, rescale, trials=100, test_ratio=0.5, k=i)
        print(f'k:{i} error:{error}')


def test4():
    samples = wine_price.wine_set2(sample_size=100)

    costf = knn.create_cost_func(knn.knn_estimate, samples)
    scale = optimization.genetic_optimize([(0, 20)] * 4, costf, pop_size=50, step=1, mut_prob=0.2, elite=0.2, max_iter=100)
    print(scale)
    rescale = knn.rescale(samples, scale)

    max_k = 5
    for i in range(1, max_k + 1):
        error = knn.cross_validation(knn.weighted_knn, rescale, trials=100, test_ratio=0.5, k=i)
        print(f'k:{i} error:{error}')


def test5():
    samples = wine_price.wine_set1(sample_size=1000)
    print(knn.prob_guess(samples, [99, 20], 40, 80))
    print(knn.prob_guess(samples, [99, 20], 80, 120))
    print(knn.prob_guess(samples, [99, 20], 120, 1000))
    print(knn.prob_guess(samples, [99, 20], 30, 120))


test5()
