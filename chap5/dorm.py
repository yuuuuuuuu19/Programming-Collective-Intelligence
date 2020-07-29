from chap5 import optimization
import math
import random

dorms = ['Zeus',
         'Athena',
         'Hercules',
         'Bacchus',
         'Pluto']

prefs = [('Toby', ('Bacchus', 'Hercules')),
         ('Steve', ('Zeus', 'Pluto')),
         ('Andrea', ('Athena', 'Zeus')),
         ('Sarah', ('Zeus', 'Pluto')),
         ('Dave', ('Athena', 'Bacchus')),
         ('Jeff', ('Pluto', 'Athena')),
         ('Fred', ('Pluto', 'Athena')),
         ('Suzie', ('Bacchus', 'Hercules')),
         ('Laura', ('Bacchus', 'Hercules')),
         ('Neil', ('Hercules', 'Athena'))]

domain = [(0, i) for i in range(len(prefs) - 1, -1, -1)]


def print_solution(sol):
    slots = []
    for i in range(len(dorms)):
        slots += [i, i]

    for i in range(len(sol)):
        val = int(sol[i])
        dorm = dorms[slots[val]]
        print(f'{prefs[i][0].rjust(6)} => {dorm}')

        del slots[val]


def dorm_cost(sol):
    cost = 0
    slots = sum([[i, i] for i in range(len(dorms))], [])

    for i in range(len(sol)):
        x = sol[i]
        dorm = dorms[slots[x]]
        pref = prefs[i][1]
        if pref[0] == dorm:
            cost += 0
        elif pref[1] == dorm:
            cost += 1
        else:
            cost += 3

        del slots[x]

    return cost



s = optimization.random_optimization(domain, dorm_cost)
print(s, dorm_cost(s))
print_solution(s)