from math import tanh
import sqlite3


class SearchNet:
    def __init__(self, db_name):
        self.con = sqlite3.connect(db_name)
        self.word_ids = None
        self.hidden_ids = None
        self.url_ids = None
        self.ai = None
        self.ah = None
        self.ao = None
        self.wi = None
        self.wo = None


        tables = self.con.execute("select * from sqlite_master where type='table'").fetchall()
        if len(tables) == 0:
            self.make_tabes()

    def __del__(self):
        self.con.close()

    def make_tabes(self):
        self.con.execute('create table hiddennode(create_key)')
        self.con.execute('create table wordhidden(fromid, toid, strength)')
        self.con.execute('create table hiddenurl(fromid, toid, strength)')
        self.con.commit()

    def get_strength(self, from_id, to_id, layer):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'

        res = self.con.execute(f'select strength from {table} where fromid={from_id} and toid={to_id}').fetchone()
        if res is None:
            if layer == 0:
                return -0.2
            if layer == 1:
                return 0
        return res[0]

    def set_strength(self, from_id, to_id, layer, strength):
        if layer == 0:
            table = 'wordhidden'
        else:
            table = 'hiddenurl'
        res = self.con.execute(f'select rowid from {table} where fromid={from_id} and toid={to_id}').fetchone()

        if res:
            row_id = res[0]
            self.con.execute(f'update {table} set strength={strength} where rowid={row_id}')
        else:
            self.con.execute(f'insert into {table} (fromid, toid, strength) values ({from_id}, {to_id}, {strength})')

    def generate_hidden_node(self, word_ids, urls):
        if len(word_ids) > 3:
            return None
        create_key = '_'.join(sorted([str(wi) for wi in word_ids]))
        res = self.con.execute(f"select rowid from hiddennode where create_key='{create_key}'").fetchone()

        # if node does'nt exist, create node
        if res is None:
            cur = self.con.execute(f"insert into hiddennode (create_key) values ('{create_key}')")
            hidden_id = cur.lastrowid
            # set default value
            for word_id in word_ids:
                self.set_strength(word_id, hidden_id, 0, 1 / len(word_ids))
            for url_id in urls:
                self.set_strength(hidden_id, url_id, 1, 0.1)

            self.con.commit()

    def get_all_hidden_ids(self, word_ids, url_ids):
        hidden_nodes = {}
        for word_id in word_ids:
            cur = self.con.execute(f'select toid from wordhidden where fromid={word_id}')
            for row in cur:
                hidden_nodes[row[0]] = 1

        for url_id in url_ids:
            cur = self.con.execute(f'select fromid from hiddenurl where toid={url_id}')
            for row in cur:
                hidden_nodes[row[0]] = 1

            return list(hidden_nodes.keys())

    def set_up_network(self, word_ids, url_ids):
        self.word_ids = word_ids
        self.url_ids = url_ids
        self.hidden_ids = self.get_all_hidden_ids(word_ids, url_ids)

        # initialize activation function values for all nodes
        # input
        self.ai = [1] * len(self.word_ids)
        # hidden
        self.ah = [1] * len(self.hidden_ids)
        # output
        self.ao = [1] * len(self.url_ids)

        # create weights matrix
        # input
        self.wi = [[self.get_strength(word_id, hidden_id, 0) for hidden_id in self.hidden_ids] for word_id in word_ids]
        # output
        self.wo = [[self.get_strength(hidden_id, url_id, 1) for url_id in self.url_ids] for hidden_id in self.hidden_ids]

    def feed_forward(self):
        # input: query words
        for i in range(len(self.word_ids)):
            self.ai[i] = 1

        # activation of hidden layer
        for i in range(len(self.hidden_ids)):
            sum = 0
            for j in range(len(self.word_ids)):
                sum += self.ai[j] * self.wi[j][i]
            self.ah[i] = tanh(sum)

        # activation of output layer
        for i in range(len(self.url_ids)):
            sum = 0
            for j in range(len(self.hidden_ids)):
                sum += self.ah[j] * self.wo[j][i]
            self.ao[i] = tanh(sum)
        return self.ao

    def get_result(self, word_ids, url_ids):
        self.set_up_network(word_ids, url_ids)
        return self.feed_forward()

    def dtanh(self, y):
        d = 1 - y ** 2
        return d

    def back_propagate(self, targets, lr=0.5):
        # calculate errors for output layer
        output_deltas = [0] * len(self.url_ids)
        for i in range(len(self.url_ids)):
            error = targets[i] - self.ao[i]
            output_deltas[i] = self.dtanh(self.ao[i]) * error

        # calculate errors for hidden layer
        hidden_deltas = [0] * len(self.hidden_ids)
        for i in range(len(self.hidden_ids)):
            error = 0
            for j in range(len(self.url_ids)):
                error += output_deltas[j] * self.wo[i][j]
            hidden_deltas[i] = self.dtanh(self.ah[i]) * error

        # update the output weights
        for i in range(len(self.hidden_ids)):
            for j in range(len(self.url_ids)):
                self.wo[i][j] += output_deltas[j] * self.ah[i] * lr

        # update the input waights
        for i in range(len(self.word_ids)):
            for j in range(len(self.hidden_ids)):
                self.wi[i][j] += hidden_deltas[j] * self.ai[j] * lr

    def train_query(self, word_ids, url_ids, selected_url):
        self.generate_hidden_node(word_ids, url_ids)
        self.set_up_network(word_ids, url_ids)
        self.feed_forward()

        targets = [0] * len(url_ids)
        targets[url_ids.index(selected_url)] = 1
        self.back_propagate(targets)
        self.update_database()

    def update_database(self):
        for i in range(len(self.word_ids)):
            for j in range(len(self.hidden_ids)):
                self.set_strength(self.word_ids[i], self.hidden_ids[j], 0, self.wi[i][j])

        for i in range(len(self.hidden_ids)):
            for j in range(len(self.url_ids)):
                self.set_strength(self.hidden_ids[i], self.url_ids[j], 1, self.wo[i][j])

        self.con.commit()
