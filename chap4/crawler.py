import urllib.request
from bs4 import BeautifulSoup
import sqlite3
import re

ignore_words = ['the', 'this', 'that', 'of', 'to', 'and', 'a', 'in', 'is', 'was', 'it', 'on', 'from']


class Crawler:
    def __init__(self, db_name):
        self.con = sqlite3.connect(db_name)
        tables = self.con.execute("select * from sqlite_master where type='table'").fetchall()
        if len(tables) == 0:
            self.create_indexed_tables()

    def __del__(self):
        self.con.close()

    def db_commit(self):
        self.con.commit()

    def create_indexed_tables(self):
        # create tables
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid, wordid, location)')
        self.con.execute('create table link(fromid integer, toid integer)')
        self.con.execute('create table linkwords(wordid, linkid)')

        # create indices
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        # commit
        self.db_commit()

    def get_entry_id(self, table, field, value, create_new=True):
        cur = self.con.execute(f"select rowid from {table} where {field}='{value}'")
        res = cur.fetchone()
        if res is None:
            if table == 'wordlist':
                print(field, value)
            cur = self.con.execute(f"insert into {table} ({field}) values ('{value}')")
            return cur.lastrowid
        else:
            return res[0]

    def add_index(self, url, soup):
        if self.is_indexed(url):
            return
        print(f'Indexing {url}')

        # get words
        text = self.get_text(soup.body)
        words = self.separate_words(text)

        # get url id
        urlid = self.get_entry_id('urllist', 'url', url)

        for i in range(len(words)):
            word = words[i]
            if word in ignore_words:
                continue
            wordid = self.get_entry_id('wordlist', 'word', word)
            self.con.execute(f'insert into wordlocation(urlid, wordid, location) values ({urlid}, {wordid}, {i})')

    def is_indexed(self, url):
        u = self.con.execute(f"select rowid from urllist where url='{url}'").fetchone()
        if u is not None:
            v = self.con.execute(f"select * from wordlocation where urlid={u[0]}").fetchone()
            if v is not None:
                return True
        return False

    def add_link_ref(self, url_from, url_to, text):
        words = self.separate_words(text)
        fromid = self.get_entry_id('urllist', 'url', url_from)
        toid = self.get_entry_id('urllist', 'url', url_to)

        if fromid == toid:
            return

        cur = self.con.execute(f'insert into link(fromid, toid) values ({fromid}, {toid})')
        linkid = cur.lastrowid
        for word in words:
            if word in ignore_words:
                continue
            wordid = self.get_entry_id('wordlist', 'word', word)
            self.con.execute(f'insert into linkwords(linkid, wordid) values ({linkid}, {wordid})')

    def crawl(self, pages, depth=2):
        for i in range(depth):
            print(f"depth {i}")
            new_pages = []
            print(len(pages))
            for page in pages:
                try:
                    c = urllib.request.urlopen(page)
                except Exception as e:
                    print(f"Failed to open {page}: {e}")
                    continue
                soup = BeautifulSoup(c.read(), 'html.parser')
                self.add_index(page, soup)

                links = soup('a')
                links = links[:10]
                for j, link in enumerate(links):
                    if 'href' in dict(link.attrs):
                        url = urllib.parse.urljoin(page, link['href'])
                        if url.find("'") != -1:
                            continue
                        print(f"\t{i},{j} {link['href']}")
                        url = url.split('#')[0]
                        if url[:4] == 'http' and not self.is_indexed(url):
                            new_pages.append(url)

                        text = self.get_text(link)
                        self.add_link_ref(page, url, text)

                self.db_commit()
            pages = new_pages

    def get_text(self, source):
        pattern = re.compile(r'>([^><\n]+?)<')
        match = pattern.findall(str(source))
        res = '\n'.join(match)
        return res

    def separate_words(self, text):
        splitter = re.compile(r'\W+')
        return [s.lower() for s in splitter.split(text) if s != ' ']
