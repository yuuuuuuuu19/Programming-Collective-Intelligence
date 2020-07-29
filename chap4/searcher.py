from chap4 import nn
import sqlite3
from collections import defaultdict


class Searcher:
    def __init__(self, db_name, nn_db):
        self.con = sqlite3.connect(db_name)
        self.nt = nn.SearchNet(nn_db)

    def __del__(self):
        self.con.close()

    def get_match_rows(self, q):
        field_list = 'w0.urlid'
        table_list = ''
        clause_list = ''
        word_ids = []

        words = q.split(' ')
        table_num = 0

        for word in words:
            # get word id
            word_row = self.con.execute(f"select rowid from wordlist where word='{word.lower()}'").fetchone()
            if word_row:
                word_id = word_row[0]
                word_ids.append(word_id)

                if table_num > 0:
                    table_list += ','
                    clause_list += ' and '
                    clause_list += f'w{table_num - 1}.urlid=w{table_num}.urlid and '

                field_list += f',w{table_num}.location'
                table_list += f'wordlocation w{table_num}'
                clause_list += f'w{table_num}.wordid={word_id}'
                table_num += 1

        if table_num == 0:
            return None, word_ids

        # construct query
        full_query = f'select {field_list} from {table_list} where {clause_list}'
        cur = self.con.execute(full_query)
        rows = [row for row in cur]

        return rows, word_ids

    def get_scored_list(self, rows, word_ids):
        total_scores = dict([(row[0], 0) for row in rows])

        weights = [(1, self.frequency_scores(rows)),
                   (1, self.location_score(rows)),
                   (1, self.distance_score(rows)),
                   (1, self.inbound_link_score(rows)),
                   (1, self.pagerank_score(rows)),
                   (1, self.link_text_score(rows, word_ids)),
                   (1, self.nn_score(rows, word_ids))]

        for weight, scores in weights:
            for url in total_scores:
                total_scores[url] += weight * scores[url]

        return total_scores

    def get_url_name(self, id):
        return self.con.execute(f'select url from urllist where rowid={id}').fetchone()[0]

    def query(self, q, n=10):
        rows, word_ids = self.get_match_rows(q)
        if rows is None:
            return
        scores = self.get_scored_list(rows, word_ids)
        ranked_scores = [(score, url) for url, score in scores.items()]
        ranked_scores.sort(reverse=True)

        for score, url_id in ranked_scores[:n]:
            linked = self.con.execute(f'select count(*) from link where toid={url_id}').fetchone()[0]
            print(f"linked by {str(linked).rjust(3)} pages => page rank:{str(score)[:5]}\tURL:{self.get_url_name(url_id)}")

        return word_ids, [r[1] for r in ranked_scores[:n]]

    def normalize_scores(self, scores, is_small_better=False):
        vsmall = 0.00001
        if is_small_better:
            min_score = min(scores.values())
            return dict([(id, min_score / max(vsmall, cnt)) for id, cnt in scores.items()])
        else:
            max_score = max(scores.values())
            if max_score == 0:
                max_score = vsmall
            return dict([(id, cnt / max_score) for id, cnt in scores.items()])

    def frequency_scores(self, rows):
        counts = defaultdict(int)
        for id, *_ in rows:
            counts[id] += 1
        return self.normalize_scores(counts)

    def location_score(self, rows):
        locations = dict([(row[0], 1000000) for row in rows])
        for row in rows:
            loc = sum(row[1:])
            if loc < locations[row[0]]:
                locations[row[0]] = loc
        return self.normalize_scores(locations, is_small_better=True)

    def distance_score(self, rows):
        if len(rows[0]) < 3:
            return dict([(row[0], 1) for row in rows])

        min_distance = dict([(row[0], 10000000) for row in rows])
        for row in rows:
            dist = sum([abs(i - j) for i, j in zip(row, row[1:])])
            if dist < min_distance[row[0]]:
                min_distance[row[0]] = dist
        return self.normalize_scores(min_distance, is_small_better=True)

    def inbound_link_score(self, rows):
        unique_urls = set(row[0] for row in rows)
        inbound_count = dict([(u, self.con.execute(f'select count(*) from link where toid={u}').fetchone()[0]) for u in unique_urls])
        return self.normalize_scores(inbound_count)

    def calulate_pagerank(self, iteration_count=20):
        # delete current pagerank table
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key, score)')

        # initialize all pagerank by 1
        self.con.execute('insert into pagerank select rowid, 1 from urllist')
        self.con.commit()

        for i in range(1, iteration_count + 1):
            print(f'{i}/{iteration_count}')
            for (urlid,) in self.con.execute('select rowid from urllist'):
                pr = 0.15

                # loop all pages links to this
                for (linker,) in self.con.execute(f'select distinct fromid from link where toid={urlid}'):
                    linkingpr = self.con.execute(f'select score from pagerank where urlid={linker}').fetchone()[0]

                    linkingcount = self.con.execute(f'select count(*) from link where fromid={linker}').fetchone()[0]
                    pr += 0.85 * linkingpr / linkingcount

                self.con.execute(f'update pagerank set score={pr} where urlid={urlid}')
            self.con.commit()

    def pagerank_score(self, rows):
        pageranks = dict([(row[0], self.con.execute(f"select score from pagerank where urlid={row[0]}").fetchone()[0]) for row in rows])
        max_pr = max(pageranks.values())
        normalized_scores = dict([(id, score / max_pr) for id, score in pageranks.items()])
        return normalized_scores

    def link_text_score(self, rows, word_ids):
        link_scores = dict([(row[0], 0) for row in rows])
        for word_id in word_ids:
            cur = self.con.execute(f'select link.fromid, link.toid from link, linkwords where wordid={word_id} and linkwords.linkid=link.rowid')
            for from_id, to_id in cur:
                if to_id in link_scores:
                    pr = self.con.execute(f'select score from pagerank where urlid={from_id}').fetchone()[0]
                    link_scores[to_id] += pr

        max_score = max(link_scores.values())
        normalized_scores = dict([(u, l / max_score) for u, l in link_scores.items()])
        return normalized_scores

    def nn_score(self, rows, word_ids):
        url_ids = list(set([row[0] for row in rows]))
        nn_res = self.nt.get_result(word_ids, url_ids)
        scores = dict([(url_ids[i], nn_res[i]) for i in range(len(url_ids))])

        return self.normalize_scores(scores)
