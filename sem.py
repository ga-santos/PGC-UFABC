from nltk.corpus import wordnet as wn


def wupSim(graph1, graph2, node1, node2):
    w1 = graph1.nodes[node1]['name'] 
    w2 = graph2.nodes[node2]['name'] 

    lst1 = w1.split()
    lst2 = w2.split()

    len1 = len(lst1)
    len2 = len(lst2)

    #TODO: verificar casos com atributos começando/terminando com espaço
    if(len1 == 0 or len2 == 0): 
        graph1.nodes[node1]['comp'] = None
        graph2.nodes[node2]['comp'] = None 
        return None
    if(len1 == 1 and len2 == 1):#caso simples 1-1
        graph1.nodes[node1]['comp'] = w1
        graph2.nodes[node2]['comp'] = w2 
        return "{:.4f}".format(retBestSense(w1, w2))
    else:
        if(len1 == 1 and len2 == 2): #caso atr1 com 1 termo atr2 2 ou mais
            edges = graph1.edges
            ancnode = -1
            for e in edges:
                if(node1 == e[1]): 
                    ancnode = e[0]
                    break
            anc = ""
            if ancnode == -1: anc = w1
            else: anc = graph1.nodes[ancnode]['name']
            w11 = anc
            w12 = w1
            w21 = lst2[0]
            w22 = lst2[1]
            if w11 == None or w12 == None or w21 == None or w22 == None:
                if w11 == None: w11 = ''
                if w12 == None: w12 = ''
                if w21 == None: w21 = ''
                if w22 == None: w22 = ''
                graph1.nodes[node1]['comp'] = ' '.join([w11, w12])
                graph2.nodes[node2]['comp'] = ' '.join([w21, w22])
                return 1.0
            graph1.nodes[node1]['comp'] = ' '.join([w11, w12])
            graph2.nodes[node2]['comp'] = ' '.join([w21, w22])
            return retAvWup(w11, w12, w21, w22)
        elif(len1 == 2 and len2 == 1):
            edges = graph2.edges
            ancnode = -1
            for e in edges:
                if(node2 == e[1]): 
                    ancnode = e[0]
                    break
            anc = ""
            if ancnode == -1: anc = w2
            else: anc = graph2.nodes[ancnode]['name']
            w11 = lst1[0]
            w12 = lst1[1]
            w21 = anc
            w22 = w2
            if w11 == None or w12 == None or w21 == None or w22 == None:
                if w11 == None: w11 = ''
                if w12 == None: w12 = ''
                if w21 == None: w21 = ''
                if w22 == None: w22 = ''
                graph1.nodes[node1]['comp'] = ' '.join([w11, w12])
                graph2.nodes[node2]['comp'] = ' '.join([w21, w22])
                return 1.0
            graph1.nodes[node1]['comp'] = ' '.join([w11, w12])
            graph2.nodes[node2]['comp'] = ' '.join([w21, w22])
            return retAvWup(w11, w12, w21, w22)
        elif(len1 == 2 and len2 == 2):
            w11 = lst1[0]
            w12 = lst1[1]
            w21 = lst2[0]
            w22 = lst2[1]
            if w11 == None or w12 == None or w21 == None or w22 == None:
                if w11 == None: w11 = ''
                if w12 == None: w12 = ''
                if w21 == None: w21 = ''
                if w22 == None: w22 = ''
                graph1.nodes[node1]['comp'] = ' '.join([w11, w12])
                graph2.nodes[node2]['comp'] = ' '.join([w21, w22])
                return 1.0
            graph1.nodes[node1]['comp'] = ' '.join([w11, w12])
            graph2.nodes[node2]['comp'] = ' '.join([w21, w22])
            return retAvWup(w11, w12, w21, w22)
        else:
            graph1.nodes[node1]['comp'] = None
            graph2.nodes[node2]['comp'] = None
            return 1.0
            


def retAvWup(w11, w12, w21, w22):
    x = retBestSense(w11, w21)
    y = retBestSense(w12, w22)
    return "{:.4f}".format((x+y)/2)

    

def retBestSense(word1, word2):
    synsets_1 = wn.synsets(word1)
    synsets_2 = wn.synsets(word2)

    if len(synsets_1) == 0 or len(synsets_2) == 0: 
        return 1.0
    
    max_sim = 0.0

    for synset_1 in synsets_1:
        for synset_2 in synsets_2:
            sim = wn.wup_similarity(synset_1, synset_2)
        if sim is not None and sim > max_sim:
            max_sim = sim
    return 1 - max_sim

def norm2(word):
    x = word.find('.')
    return word[0:x]


