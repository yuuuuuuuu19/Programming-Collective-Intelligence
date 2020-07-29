import random
import math
import time
from collections import defaultdict
from chap5 import optimization

people = [('Seymour', "BOS"),
          ('Franny', "DAL"),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('LES', 'OMA')]

flights = defaultdict(list)
with open('./schedule.txt', 'r') as f:
    lines = f.read().split('\n')
    for line in lines:
        origin, destination, depart, arrive, price = line.split(',')
        flights[(origin, destination)].append([depart, arrive, int(price)])


def get_minutes(t):
    x = time.strptime(t, '%H:%M')
    hours = x[3]
    minutes = x[4]
    return 60 * hours + minutes


def print_schedule(schedule, destination='LGA'):
    ops = schedule[::2]
    rps = schedule[1::2]
    for name_origin, i, j in zip(people, ops, rps):
        name = name_origin[0]
        origin = name_origin[1]
        op = flights[(origin, destination)][i]
        rp = flights[(destination, origin)][j]
        print(f'name: {name.ljust(8)} from {origin}\n\toutward path | {op[0].rjust(5)} => {op[1].rjust(5)} | ${op[2]}\n\treturn path  | {rp[0].rjust(5)} => {rp[1].rjust(5)} | ${rp[2]}')


def schedule_cost(sol, destination='LGA'):
    total_price = 0
    latest_arrival = 0
    earliest_dep = 24 * 60

    ops = sol[::2]
    rps = sol[1::2]

    arrives = []
    leaves = []

    for (name, origin), i, j in zip(people, ops, rps):
        op = flights[(origin, destination)][i]
        rp = flights[(destination, origin)][j]

        arrives.append(op[1])
        leaves.append(rp[0])

        total_price += op[2] + rp[2]

        latest_arrival = max(latest_arrival, get_minutes(op[1]))
        earliest_dep = min(earliest_dep, get_minutes(rp[0]))

    total_wait = 0
    total_wait += sum(latest_arrival - get_minutes(arrive) for arrive in arrives)
    total_wait += sum(get_minutes(leave) - earliest_dep for leave in leaves)

    if latest_arrival < earliest_dep:
        total_price += 50

    total_cost = total_price + total_wait
    return total_cost



def test():
    schedule = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3]
    print_schedule(schedule)
    print(schedule, schedule_cost(schedule))
    domain = [(0, 9)] * len((people)) * 2
    s = optimization.random_optimization(domain, schedule_cost, iter_count=10000)
    print(s, schedule_cost(s), 'random optimization')
    t = optimization.hillclimb(domain, schedule_cost)
    print(t, schedule_cost(t), 'hill climb')
    u = optimization.annealing_optimize(domain, schedule_cost, T=10000, cooling_rate=0.85)
    print(u, schedule_cost(u), 'annealing')
    v = optimization.genetic_optimize(domain, schedule_cost, pop_size=100, step=1, mut_prob=0.3, elite=0.2, max_iter=1000)
    print(v, schedule_cost(v), 'genetic optimization')

test()