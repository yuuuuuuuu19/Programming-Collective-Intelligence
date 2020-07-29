from chap11 import gp, grid_game
import matplotlib.pyplot as plt
import numpy as np

addw = gp.FunctionWrapper(lambda op: op[0] + op[1], 2, 'add')
subw = gp.FunctionWrapper(lambda op: op[0] - op[1], 2, 'sub')
mulw = gp.FunctionWrapper(lambda op: op[0] * op[1], 2, 'mul')

ifw = gp.FunctionWrapper(lambda op: [op[1], op[2]][op[0] > 0], 3, 'if')
gtw = gp.FunctionWrapper(lambda op: op[0] > op[1], 2, 'isgreater')

func_list = [addw, subw, mulw, ifw, gtw]


def test():
    gtn = gp.Node(gtw, [gp.ParamNode(0), gp.ConstNode(3)])
    adn = gp.Node(addw, [gp.ParamNode(1), gp.ConstNode(5)])
    sbn = gp.Node(subw, [gp.ParamNode(1), gp.ConstNode(2)])

    tree_exame = gp.Node(ifw, [gtn, adn, sbn])


def test2(n=10):
    random_tree = gp.make_random_tree(2, function_list=func_list)
    random_tree2 = gp.make_random_tree(2, function_list=func_list)

    hidden_testset = gp.build_hidden_testset(300)

    print('error', gp.score_function(random_tree, hidden_testset))
    print('error', gp.score_function(random_tree2, hidden_testset))
    print()

    mutate1 = gp.mutate(random_tree, 2, probability=0.5)
    mutate2 = gp.mutate(random_tree2, 2, probability=0.5)

    print('error', gp.score_function(mutate1, hidden_testset))
    print('error', gp.score_function(mutate2, hidden_testset))
    print()

    cross1 = gp.crossover(random_tree, random_tree2)
    cross2 = gp.crossover(mutate1, mutate2)

    print('error', gp.score_function(cross1, hidden_testset))
    print('error', gp.score_function(cross2, hidden_testset))

    rf = gp.get_rank_function(gp.build_hidden_testset(test_size=300))

    res = []
    for i in range(n):
        log = gp.evolve(2, 100, rf, max_generation=100, mutate_rate=0.2, breeding_rate=0.2, prob_exp=0.7, prob_new=0.1)
        res.append(log)

    return res


def test3():
    logs = test2(n=10)
    f = plt.figure()
    for log in logs:
        data = np.array(log)
        generations, scores = data[:, 0], data[:, 1]
        plt.plot(generations, np.log10(scores), marker='x')

    plt.xlabel('Generation')
    plt.ylabel('diff')
    f.savefig('generation4.png')
    plt.show()


def test4():
    p1 = gp.make_random_tree(5, func_list)
    p2 = gp.make_random_tree(5, func_list)

    #grid_game.grid_game([p1, p2], n=5, limit=50)
    winner = gp.evolve(5, 100, grid_game.tournament, max_generation=50)


test4()
