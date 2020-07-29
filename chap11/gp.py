import random
from copy import deepcopy
import math


class FunctionWrapper:
    def __init__(self, function, child_count, name):
        self.function = function
        self.child_node = child_count
        self.child_count = child_count
        self.name = name


class Node:
    def __init__(self, function_wrapper, children):
        self.function = function_wrapper.function
        self.children = children

    def evaluate(self, params):
        results = [n.evaluate(params) for n in self.children]
        return self.function(results)


class ParamNode:
    def __init__(self, idx):
        self.idx = idx

    def evaluate(self, params):
        return params[self.idx]


class ConstNode:
    def __init__(self, value):
        self.value = value

    def evaluate(self, params):
        return self.value


addw = FunctionWrapper(lambda op: op[0] + op[1], 2, 'add')
subw = FunctionWrapper(lambda op: op[0] - op[1], 2, 'sub')
mulw = FunctionWrapper(lambda op: op[0] * op[1], 2, 'mul')

ifw = FunctionWrapper(lambda op: [op[1], op[2]][op[0] > 0], 3, 'if')
gtw = FunctionWrapper(lambda op: op[0] > op[1], 2, 'isgreater')

func_list = [addw, subw, mulw, ifw, gtw]


def make_random_tree(params_count, function_list, max_depth=4, function_prob=0.5, params_prob=0.6):
    if random.random() < function_prob and max_depth > 0:
        function = random.choice(function_list)
        children = [make_random_tree(params_count, function_list, max_depth - 1, function_prob, params_prob) for i in range(function.child_count)]
        return Node(function, children)
    elif random.random() < params_prob:
        return ParamNode(random.randint(0, params_count - 1))
    else:
        return ConstNode(random.randint(0, 10))


def hidden_function(x, y):
    return x ** 2 + 3 * x + 2 * y + 5


def build_hidden_testset(test_size):
    rows = []
    for i in range(test_size):
        x, y = random.randint(0, 40), random.randint(0, 40)
        rows.append([x, y, hidden_function(x, y)])
    return rows


def score_function(tree, s):
    dif = 0
    total_res = 0
    total_ans = 0
    for data in s:
        v = tree.evaluate([data[0], data[1]])
        total_res += v
        total_ans += data[2]
        dif += abs(v - data[2])

    return dif


def mutate(tree, param_count, probability=0.1):
    if random.random() < probability:
        return make_random_tree(param_count, func_list)
    else:
        result = deepcopy(tree)
        if hasattr(tree, 'children'):
            result.childen = [mutate(child, param_count, probability) for child in tree.children]
        return result


def crossover(tree1, tree2, probswap=0.7, top=1):
    if random.random() < probswap and not top:
        return deepcopy(tree2)
    else:
        result = deepcopy(tree1)
        if hasattr(tree1, 'children') and hasattr(tree2, 'children'):
            result.children = [crossover(c, random.choice(tree2.children), probswap, 0) for c in tree1.children]
        return result


def evolve(param_count, popsize, rank_function, max_generation=500, mutate_rate=0.1, breeding_rate=0.1, prob_exp=0.7, prob_new=0.05):
    def select_index():
        return int(math.log(random.random()) / math.log(prob_exp))

    population = [make_random_tree(param_count, func_list) for i in range(popsize)]
    log = []
    for i in range(max_generation):

        scores = rank_function(population)
        new_pop = [scores[0][1], scores[1][1]]

        best_score = scores[0][0]
        print(f"generation {i} score: {best_score}")
        log.append([i, best_score])
        if best_score == 0:
            break

        # next generation
        while len(new_pop) < popsize:
            if random.random() > prob_new:
                new_pop.append(mutate(
                    crossover(scores[select_index()][1],
                              scores[select_index()][1],
                              probswap=breeding_rate),
                    param_count,
                    probability=mutate_rate))
            else:
                new_pop.append(make_random_tree(param_count, func_list))

        population = new_pop

    return log


def get_rank_function(dataset):
    def rank_function(population):
        scores = [(score_function(tree, dataset), tree) for tree in population]
        scores.sort(key=lambda x: x[0])
        return scores

    return rank_function
