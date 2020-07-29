import random
import math


def random_optimization(domain, costf, iter_count=1000):
    best = 100000000
    best_r = None
    for i in range(iter_count):
        r = [random.randint(domain[i][0], domain[i][1]) for i in range(len(domain))]

        cost = costf(r)

        if cost < best:
            best = cost
            best_r = r

    return best_r


def hillclimb(domain, costf):
    n = len(domain)
    sol = [random.randint(domain[i][0], domain[i][1]) for i in range(n)]

    while 1:
        neighbors = []
        for i in range(n):
            if domain[i][0] < sol[i]:
                neighbors.append(sol[:i] + [sol[i] - 1] + sol[i + 1:])
            if domain[i][1] > sol[i]:
                neighbors.append(sol[:i] + [sol[i] + 1] + sol[i + 1:])

        current = costf(sol)
        best = current
        for i in range(len(neighbors)):
            cost = costf(neighbors[i])
            if cost < best:
                best = cost
                sol = neighbors[i]

        if best == current:
            break

    return sol


def annealing_optimize(domain, costf, T=10000, cooling_rate=0.95, step=1):
    n = len(domain)
    e = math.e
    # random initialization
    vec = [random.randint(domain[i][0], domain[i][1]) for i in range(n)]
    ea = costf(vec)

    while T > 0.1:
        # select index
        i = random.randint(0, n - 1)

        dir = random.randint(-step, step)

        vecb = vec
        vecb[i] += dir
        vecb[i] = min(max(domain[i][0], vecb[i]), domain[i][1])

        eb = costf(vecb)
        x = -abs(eb - ea) / T
        p = pow(e, x)

        if eb < ea or random.random() < p:
            vec = vecb
            ea = eb

        T *= cooling_rate

    return vec


def genetic_optimize(domain, costf, pop_size=50, step=1, mut_prob=0.2, elite=0.2, max_iter=100):

    def mutate(vec):
        i = random.randint(0, len(domain) - 1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[:i] + [vec[i] - step] + vec[i + 1:]
        elif vec[i] < domain[i][1]:
            return vec[:i] + [vec[i] + step] + vec[i+1:]
        else:
            return vec

    def crossover(r1, r2):
        i = random.randint(1, len(domain) - 2)
        return r1[:i] + r2[i:]

    n = len(domain)
    pop = [[random.randint(domain[i][0], domain[i][1]) for i in range(n)] for _ in range(pop_size)]
    top_elite = int(elite * pop_size)

    for i in range(max_iter):
        scores = [(costf(v), v) for v in pop if v]
        scores.sort()
        ranked = [v for _, v in scores]

        pop = ranked[:top_elite]

        while len(pop) < pop_size:
            if random.random() < mut_prob:
                # mutate
                c = random.randint(0, top_elite)
                pop.append(mutate(ranked[c]))
            else:
                # crossover
                c1 = random.randint(0, top_elite)
                c2 = random.randint(0, top_elite)
                pop.append(crossover(ranked[c1], ranked[c2]))

        #print(f'\ttop score: {scores[0][0]}')

    return scores[0][1]
