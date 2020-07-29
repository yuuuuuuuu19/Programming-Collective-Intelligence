from chap3 import clusters, dendrogram, draw2d


def test():
    url = "https://raw.githubusercontent.com/arthur-e/Programming-Collective-Intelligence/master/chapter3/blogdata.txt"
    data = clusters.readfile(url)
    cols = data["cols"]
    labels = data["rows"]
    table = data["table"]

    clusts = clusters.hcluster(table)

    root = clusts[-1]

    dummy_label = [str(i) for i in range(len(labels) * 2 - 1)]
    #clusters.print_node(root, dummy_label)
    #dendrogram.draw_dendrogram(root, labels)

    clustering_by_kmeans = clusters.k_means_clustering(table, k=10)
    for i, cluster in enumerate(clustering_by_kmeans):
        print(f"cluster {i}")
        for id in cluster:
            print("\t"+labels[id])

    data = clusters.scale_down(table, rate=0.01, max_iteration=500)
    draw2d.draw_2d(data, labels)

test()