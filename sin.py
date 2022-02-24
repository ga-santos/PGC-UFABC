from similarity.normalized_levenshtein import NormalizedLevenshtein
from similarity.jarowinkler import JaroWinkler

# Usando distancia (0 = igual)

def compJaroWink(graph1, graph2, node1, node2):
    jr = JaroWinkler()
    return "{:.4f}".format(jr.distance(graph1.nodes[node1]['name'], graph2.nodes[node2]['name']))

def compLeven(graph1, graph2, node1, node2):
    lv = NormalizedLevenshtein()
    return "{:.4f}".format(lv.distance(graph1.nodes[node1]['name'], graph2.nodes[node2]['name']))
