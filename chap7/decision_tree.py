from collections import defaultdict, Counter
import math
import sys

sys.setrecursionlimit(100000)


class DecisionNode:

    # col -> index of classification variable
    #        ?
    #     /     \    <= threshold value
    #   true   false

    def __init__(self, col=-1, value=None, results=None, true_branch=None, false_branch=None):
        self.col = col
        self.value = value
        self.results = results
        self.true_branch = true_branch
        self.false_branch = false_branch


# split a set by specific item(column) -> row
def divide_set(rows, column, value):
    split_func = None

    # type of threshold value
    # case of numerical value
    if isinstance(value, int) or isinstance(value, float):
        split_func = lambda row: row[column] >= value
    # non-numerical value
    else:
        split_func = lambda row: row[column] == value

    *set1, = filter(split_func, rows)
    set2 = [i for i in rows if i not in set1]

    return (set1, set2)


def unique_counts(rows):
    *res, = map(lambda x: x[-1], rows)
    return dict(Counter(res))


def variance(rows):
    n = len(rows)
    if n == 0:
        return 0
    data = [row[-1] for row in rows]
    m = sum(data) / n
    var = sum(pow(x - m, 2) for x in data)
    return var

def gini_inpurity(rows):
    n = len(rows)
    counts = unique_counts(rows)
    imp = 1
    for c in counts.values():
        imp -= pow(c / n, 2)

    return imp


def entropy(rows):
    n = len(rows)
    res = unique_counts(rows)

    ent = 0
    for c in res.values():
        p = c / n
        ent += -p * math.log2(p)

    return ent


def build_tree(rows, scoref=entropy):
    n = len(rows)
    if n == 0:
        return DecisionNode()

    current_score = scoref(rows)

    best_gain = 0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(column_count):
        column_values = dict([(row[col], 1) for row in rows])
        for value in column_values.keys():
            set1, set2 = divide_set(rows, col, value)
            p = len(set1) / n
            # information gain
            gain = current_score - (p * scoref(set1) + (1 - p) * scoref(set2))
            if gain > best_gain and len(set1) * len(set2) > 0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)

    if best_gain > 0:
        true_branch = build_tree(best_sets[0])
        false_branch = build_tree(best_sets[1])
        return DecisionNode(col=best_criteria[0], value=best_criteria[1], true_branch=true_branch, false_branch=false_branch)
    else:
        return DecisionNode(results=unique_counts(rows))


def classify(observation, node):
    if node.results is not None:
        return node.results
    else:
        v = observation[node.col]
        branch = None
        if isinstance(v, int) or isinstance(v, float):
            if v >= node.value:
                branch = node.true_branch
            else:
                branch = node.false_branch

        else:
            if v == node.value:
                branch = node.true_branch
            else:
                branch = node.false_branch

        return classify(observation, branch)


def md_classify(observation, node):
    if node.results is not None:
        return node.results
    else:
        v = observation[node.col]
        if v is None:
            true_branch = md_classify(observation, node.true_branch)
            false_branch = md_classify(observation, node.false_branch)

            true_count = sum(true_branch.values())
            false_count = sum(false_branch.values())

            true_weight = true_count / (true_count + false_count)
            false_weight = false_count / (true_count + false_count)

            res = {}
            for k, v in true_branch.items():
                res[k] = v * true_weight
            for k, v in false_branch.items():
                res[k] = v * false_weight

            return res
        else:
            if isinstance(v, int) or isinstance(v, float):
                if v >= node.value:
                    branch = node.true_branch
                else:
                    branch = node.false_branch
            else:
                if v == node.value:
                    branch = node.true_branch
                else:
                    branch = node.false_branch

            return md_classify(observation, branch)


def prune(node, threshold):
    if node.true_branch.results is None:
        prune(node.true_branch, threshold)
    if node.false_branch.results is None:
        prune(node.false_branch, threshold)

    if node.true_branch.results is not None and node.false_branch.results is not None:
        true_branch, false_branch = [], []
        for res, cnt in node.true_branch.results.items():
            true_branch += [[res]] * cnt
        for res, cnt in node.false_branch.results.items():
            false_branch += [[res]] * cnt

        delta = entropy(true_branch + false_branch) - (entropy(true_branch) + entropy(false_branch)) / 2
        if delta < threshold:
            # merging back branches
            node.true_branch = node.false_branch = None
            node.results = unique_counts(true_branch + false_branch)
