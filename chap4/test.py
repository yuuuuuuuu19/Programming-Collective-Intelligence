from chap4 import crawler, searcher, nn


def test_crawler():
    pages = ['https://time.com/']
    crw = crawler.Crawler('search_index.db')
    crw.crawl(pages)

    wordlocation = crw.con.execute("select rowid from wordlocation where wordid=1")
    print(wordlocation)



def test_searcher():
    sch = searcher.Searcher('search_index.db', 'nn_db')
    # q = sch.get_match_rows('covid-19 world')
    #sch.calulate_pagerank(iteration_count=50)
    sch.query('matter covid', 50)


def test_nn():
    mynet = nn.SearchNet('nn.db')
    w_a, w_b, w_c = 101, 102, 103
    u_a, u_b, u_c = 201, 202, 203
    mynet.generate_hidden_node([w_a, w_c], [u_a, u_b, u_c])

    for c in mynet.con.execute('select * from wordhidden'):
        print(c)
    print()

    for c in mynet.con.execute('select * from hiddenurl'):
        print(c)


    mynet.train_query([w_a, w_c], [u_a, u_b, u_c], u_a)
    res = mynet.get_result([w_a, w_c], [u_a, u_b, u_c])
    print(res)

#test_crawler()
test_searcher()
#test_nn()
