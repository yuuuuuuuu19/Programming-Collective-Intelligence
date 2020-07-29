from chap7 import decision_tree, draw_tree, zillow


def test():
    load = None
    with open('./decision_tree_example.txt', 'r') as f:
        load = f.read()

    data = [line.split() for line in load.split('\n')]

    divided = decision_tree.divide_set(data, 2, 'yes')
    print(divided[0])
    print(divided[1])
    print(decision_tree.gini_inpurity(data))
    print(decision_tree.entropy(data))

    print(decision_tree.gini_inpurity(divided[0]))
    print(decision_tree.gini_inpurity(divided[1]))

    print(decision_tree.entropy(divided[0]))
    print(decision_tree.entropy(divided[1]))

    root = decision_tree.build_tree(data)
    draw_tree.print_tree(root)

    draw_tree.draw_tree(root, 'tree')


def test2():
    load = None
    with open('./decision_tree_example.txt', 'r') as f:
        load = f.read()

    data = [line.split() for line in load.split('\n')]

    root = decision_tree.build_tree(data)
    observation = ['(direct)', 'USA', 'yes', 5]
    res = decision_tree.classify(observation, root)
    print(res)
    draw_tree.print_tree(root)
    decision_tree.prune(root, 1)
    draw_tree.print_tree(root)


def test3():
    load = None
    with open('./decision_tree_example.txt', 'r') as f:
        load = f.read()

    data = [line.split() for line in load.split('\n')]

    root = decision_tree.build_tree(data)
    observation = ['google', None, 'yes', None]
    res = decision_tree.md_classify(observation, root)
    print(res)

    observation = ['google', 'France', None, None]
    res = decision_tree.md_classify(observation, root)
    print(res)

def test4():
    house_data = zillow.get_pricelist()
    print(house_data,'?')
    root = decision_tree.build_tree(house_data, scoref=decision_tree.variance)
    draw_tree.print_tree(root)
    draw_tree.draw_tree(root, 'house-tree')

test4()
