import math
import sqlite3


class Classifier:
    def __init__(self, get_features, db_name, file_name=None):
        self.get_features = get_features
        self.file_name = file_name
        self.feature_count = {}
        self.cc = {}
        self.set_db(db_name)

    def set_db(self, db_name):
        self.con = sqlite3.connect(db_name)
        self.con.execute('create table if not exists fc(feature, category, count)')
        self.con.execute('create table if not exists cc(category, count)')

    # increment the count of feature/category pair
    def incf(self, f, cat):
        count = self.fcount(f, cat)
        if count == 0:
            self.con.execute(f"insert into fc values ('{f}', '{cat}', 1)")
        else:
            self.con.execute(f"update fc set count={count + 1} where feature='{f}' and category='{cat}'")

    # increment the count of a category
    # f: feature
    # cat: category
    def incc(self, cat):
        count = self.cat_count(cat)
        if count == 0:
            self.con.execute(f"insert into cc values ('{cat}', 1)")
        else:
            self.con.execute(f"update cc set count={count + 1} where category='{cat}'")

    # return number of feature in a document
    def fcount(self, f, cat):
        res = self.con.execute(f"select count from fc where feature='{f}' and category='{cat}'").fetchone()
        if res is None:
            return 0
        else:
            return res[0]

    # return number of item in a category
    def cat_count(self, cat):
        res = self.con.execute(f"select count from cc where category='{cat}'").fetchone()
        if res is None:
            return 0
        else:
            return res[0]

    # return total number of items
    def total_count(self):
        res = self.con.execute(f"select sum(count) from cc").fetchone()
        if res is None:
            return 0
        return res[0]

    # return list of categories
    def get_categories(self):
        cur = self.con.execute(f"select category from cc")
        return [d[0] for d in cur]

    def fprob(self, f, cat):
        if self.cat_count(cat) == 0:
            return 0
        prob = self.fcount(f, cat) / self.cat_count(cat)
        return prob

    def weighted_prob(self, f, cat, prf, weight=1, ap=0.5):
        # current probability
        basic_prob = prf(f, cat)

        # counts the number of times this feature appeared in all categories
        total = sum(self.fcount(f, cat_) for cat_ in self.get_categories())

        # calculate weighted average
        bp = ((weight * ap) + (total * basic_prob)) / (weight + total)
        return bp

    def train(self, item, cat):
        features = self.get_features(item)
        # increment the count for every feature with this category
        for feature in features:
            self.incf(feature, cat)
        # increment the count for this category
        self.incc(cat)
        self.con.commit()


class NaiveBayes(Classifier):
    def __init__(self, get_features, db_name, file_name=None):
        super().__init__(get_features, db_name, file_name)
        self.thresholds = {}

    def doc_prob(self, item, cat):
        features = self.get_features(item)
        # multiply all probability
        p = 1
        for f in features:
            p *= self.weighted_prob(f, cat, self.fprob)

        return p

    def prob(self, item, cat):
        cat_prob = self.cat_count(cat) / self.total_count()
        doc_prob = self.doc_prob(item, cat)
        return doc_prob * cat_prob

    def set_threshold(self, cat, t):
        self.thresholds[cat] = t

    def get_threshold(self, cat):
        if cat not in self.thresholds:
            return 1
        return self.thresholds[cat]

    def classify(self, item, default=None):
        probs = {}
        max_ = 0
        best = None

        for cat in self.get_categories():
            probs[cat] = self.prob(item, cat)
            if probs[cat] > max_:
                max_ = probs[cat]
                best = cat

        for cat in probs.keys():
            if cat == best:
                continue
            if probs[cat] * self.get_threshold(best) > probs[best]:
                return default
        return best


class FisherClassifier(Classifier):
    def __init__(self, get_features, db_name, file_name=None):
        super().__init__(get_features, db_name, file_name)
        self.minimums = {}

    def set_minimumus(self, cat, min):
        self.minimums[cat] = min

    def get_minimumus(self, cat):
        if cat not in self.minimums:
            return 0
        return self.minimums[cat]

    def cprob(self, f, cat):
        # feature frequency in this category
        clf = self.fprob(f, cat)
        if clf == 0:
            return 0

        # feature frequency in all categories
        # good python: x
        # bad python: y
        # probability of good python => x/(x+y)
        freq_sum = sum(self.fprob(f, c) for c in self.get_categories())
        p = clf / freq_sum
        return p

    def fisher_prob(self, item, cat):
        # multiply all probability
        p = 1
        features = self.get_features(item)
        for f in features:
            p *= self.weighted_prob(f, cat, self.cprob)

        f_score = -2 * math.log(p)

        return self.invhi2(f_score, len(features) * 2)

    def invhi2(self, chi, df):
        m = chi / 2
        s = math.exp(-m)
        term = math.exp(-m)
        for i in range(1, df // 2):
            term *= m / i
            s += term

        return min(s, 1)

    def classify(self, item, default=None):
        best = default
        max_ = 0
        for c in self.get_categories():
            p = self.fisher_prob(item, c)
            if p > self.get_minimumus(c) and p > max_:
                best = c
                max_ = p
        return best
