

    # data is the output from 'returnDataList()'
    # data = [[n, "...", "...", "..."],
    #         [m, "...", "...", "..."],
    #           ....   ....   ....   ]

    # (schema, graph, nodes) => returnDataList() => [[n, "...", "...", "..."],
    #                                                [m, "...", "...", "..."]]
    #
    #     [[n, "...", "...", "..."],
    #      [m, "...", "...", "..."],  => returnAver() => [[n, av, dp, "..."],
    #        ....   ....   ....   ]                       [m, av, dp, "..."]]            
    #
    #      [[n, av, dp, "..."],        => buildHist() => [[n, av, dp, [f1, f2, f3, ....],
    #       [m, av, dp, "..."]]                           [m, av, dp, [f1, f2, f3, ....]]
    #
    #
    #        FALTANDO A NORMDATA COM NORMHIST
    #
    #      [[n, av, dp, [f1, f2, f3, ....],  => applyData2Graph() => grafo com atributo 'hist', contendo a lista
    #       [m, av, dp, [f1, f2, f3, ....]]                                     [av, dp, [f1, f2, f3, ....]]
    #
    #


import os
from collections import Counter
from scipy.stats import wasserstein_distance



def compData(graph1, graph2, node1, node2):
    if graph1.nodes[node1]['data'] != None and graph2.nodes[node2]['data'] != None: 
        #a = compHistWass(graph1.nodes[node1]['data'][2], graph2.nodes[node2]['data'][2])
        h = compDiff(graph1.nodes[node1]['data'][2], graph2.nodes[node2]['data'][2])
        #o = compDistOrd(graph1.nodes[node1]['data'][2], graph2.nodes[node2]['data'][2])
        dav = abs(graph1.nodes[node1]['data'][0] - graph2.nodes[node2]['data'][0])
        ddp = abs(graph1.nodes[node1]['data'][1] - graph2.nodes[node2]['data'][1])
        return ["{:.4f}".format(dav),"{:.4f}".format(ddp), "{:.5f}".format(h)]
    return [None, None, None, None] 


def compHistWass(hist1, hist2):
    if len(hist1) != len(hist2): return -1
    return wasserstein_distance(hist1, hist2)

def compDistOrd(hist1, hist2):
    if len(hist1)!= len(hist2): return -1
    res = 0
    h = 0
    for i in range(0, len(hist1)):
        res += hist1[i] - hist2[i]
        h += abs(res)
    return h

def compDiff(hist1, hist2):
    if len(hist1)!= len(hist2): return -1
    res = 0
    for i in range(0, len(hist1)):
        res += abs(hist1[i] - hist2[i])
    return res


def normData(data):
    if data == None: return None
    for i in data:
        if len(i) <= 2:
            continue
        else:
            i[3] = normHist(i[3])
    return data

def normHist(hist):
    maxh = 0
    minh = hist[0]
    for i in hist: 
        if i > maxh: maxh = i
        if i < minh: minh = i
    for i in range(0, len(hist)):
        hist[i] = ((hist[i] - minh)/(maxh - minh))
    return hist



def formatName(name):
    a = name.rfind('/')
    b = name.rfind('.')
    return name[a+1:b]

def applyData2Graph(data, graph, nodes):
    print('apply data')
    if data == None:
        for i in range(0, nodes):
            graph.nodes[i]['data'] = None
    else:
        for item in data:
            if len(item) <= 2: 
                graph.nodes[item[0]]['data'] = None
            else: 
                graph.nodes[item[0]]['data'] = [item[1], item[2], item[3]]

def returnAver(lst):
    print('return average')
    #print('Iniciando returnAver() ... .. .')
    # lst = [[n, "...", "...", "..."], 
    #        [m, "...", "...", "..."] ]                     ]]
    final = []
    # final = [[n, av, avv, "..."], [m, av, avv, "..."], ... ]
    if lst == None: return None
    for item in lst: # item é [n, "...", "..."]
        if len(item) <= 1:
            prov = [item[0]]
            final.append(prov)
            continue
        else:
            tmp = [] # tmp é [len1, len2, len3, ...]

            # calcula os comprimentos e guarda em tmp
            for i in range(1, len(item)):
                tmp.append(len(item[i]))
            
            #calcula as medias e guarda em av
            av = 0
            for k in range(0, len(tmp)):
                av += tmp[k]
            av /= len(tmp)
            
            # calcula o desvio de cada medida e guarda em tmp2
            dp = 0
            for i in range(0, len(tmp)):
                dp += abs(av - tmp[i])
            dp /= len(tmp)

            prov = [item[0], av, dp, ""]
            for i in range(1, len(item)):
                prov[3] += item[i]

            final.append(prov)
    return final

        
            

def buildHist(data):
    print('build hist')
    if data == None: return None
    #print('Iniciando buildHist() ... .. .')
    alpha = "0123456789 abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&'()*+,-./:;<=>?@[\]^_'{}|~"
    # data = [[n, av, dp, "..."],
    #         [m, av, dp, "..."]]

    cnt = []
    for i in data:
        if len(i) <= 1:
            cnt.append(None)
            continue
        else:
            cnt.append(Counter(i[3]))
    # cnt = [Counter("......"),
    #        Counter("......")]

    for i in range(0, len(cnt)):
        if cnt[i] == None:
            # poderia ser data[i][1] mas como esse elemento nao existe.....
            data[i].append(None)
            continue
        else: 
            tmp = []
            #tmp terá as contagens dos simbolos
            for x in alpha:
                c = cnt[i].get(x)
                if c == None: tmp.append(0)
                else: tmp.append(c)
            # substitui os dados brutos pela contagem dos simbolos na lista original 'data'
            data[i][3] = tmp
            tmp = []
            #teoricamente tudo OK ate aqui

        #[[n, av, dp, [f1, f2, f3, ....],
        # [m, av, dp, [f1, f2, f3, ....]]
    return data 

def removeSpaces(js):# incluir para \t também?
    ret = ''
    f = 1
    for i in js:
        if ((i == ' ' or i == '\n') and f == 1): continue
        elif(i == '"'):
            ret += i
            f *= -1
        else: ret +=i
    return ret

def retDocEnd(js):
    c = 0
    stack = []
    for i in range(0, len(js)):
        if js[i] == '{':
            stack.append('.')
        elif js[i] == '}': 
            stack.pop()
        if len(stack) == 0:
            c = i
            break
    return c

def retDocEndArr(js):
    c = 0
    stack = []
    for i in range(0, len(js)):
        if js[i] == '[':stack.append('.')
        elif js[i] == ']': stack.pop()
        if len(stack) == 0:
            c = i
            break
    return c



def returnDataList(schema, graph, nodes):
    print('return data list')
    pth = 'documents/' + formatName(schema) + '-file' + '.json'
    if os.path.isfile(pth) == False: return None
    js = ""
    with open(pth, "r") as f:
        js = f.read()
        js = removeSpaces(js)
        js = js.replace("\t", "")
        js = js.replace("\n", "")
    
    attrlist = []
    for x in range(0, nodes):
        attrlist.append([x])

    start = 1
    while True:
        x = 0
        search = 0
        last = 0
        startsub = 1
        end = start + retDocEnd(js[start:])
        sec = js[start:end+1]
        #OK
        while x < nodes:
            if graph.nodes[x]['type'] == 'object':
                x+=1
                continue
                #OK
            elif graph.nodes[x]['type'] == 'array':
                t = sec.find('"'+graph.nodes[x]['name']+'":', search) + len('"'+graph.nodes[x]['name']+'":')
                r = t + retDocEndArr(sec[t:])
                sec2 = sec[t:r+1]
                #TECNICAMENTE OK
                search = r+2
                k = []
                startsub = 1
                for i in graph.edges:
                    if i[0] == x:k.append(i[1])
                #TECNICAMENTE OK
                if len(k) == 0: #
                    sec2 = sec2[1:len(sec2)-1]
                    sec2  = sec2.replace('"', '')
                    div = sec2.split(',')
                    for h in div:
                        attrlist[x].append[h]
                else:
                    #CALCULO CORRETO
                    while True:
                        endsub = startsub + retDocEnd(sec2[startsub:])
                        secsub = sec2[startsub:endsub+1]
                        for i in range(0, len(k)):    
                            fnd = '"'+graph.nodes[x+i+1]['name']+'":'
                            ind = secsub.find(fnd, 0) + len(fnd)
                            if(secsub[ind]=='"'):
                                ind+=1
                                a = secsub.find('"', ind)
                                attrlist[x+i+1].append(secsub[ind:a])
                            else:
                                a = secsub.find(',', ind)
                                b = secsub.find('}', ind)
                                if a == -1: a = b   
                                if b < a: a = b
                                attrlist[x+i+1].append(secsub[ind:a])
                                if i == len(k) - 1: last = x+i+1
                        if sec2[endsub+1]==',':
                            startsub = endsub + 2
                            continue
                        else:break
                    x = last
            else:
                fnd = '"'+graph.nodes[x]['name']+'":'
                ind = sec.find(fnd, 0) + len(fnd) - 1
                if(sec[ind+1]=='"'):
                    ind+=2
                    a = sec.find('"', ind)
                    attrlist[x].append(sec[ind:a])
                else:
                    ind+=1
                    a = sec.find(',', ind)
                    b = sec.find('}', ind)
                    if a == -1: a = b
                    if b < a: a = b
                    attrlist[x].append(sec[ind:a])              
            x+=1
        if js[end+1]==',':
            start = end + 2
            continue
        else:break
    #[print(g[0]) for g in attrlist]
    return attrlist





def returnDataList2(schema, graph, nodes):
    # Schema -> schema.json
    # Docs   -> schema1.json, schema2.json .....
    #print('iniciando returnDataList() ... .. .')
    allfiles = os.listdir('documents/' + formatName(schema) + '/') # TODO incluir só arquivos
    if allfiles == False : return None
    
    attrlist = []
    for i in range(0, nodes): # Deve ter outro jeito melhor obvio, mas foi o melhor que deu pra fazer
        if graph.nodes[i]['type'] != 'array' or graph.nodes[i]['type'] != 'object': attrlist.append([i])
    
    lastind = 0
    for x in allfiles: # retirar no futuro
        lastind = 0
        path = 'documents/' + formatName(schema) + '/' + str(x)
        js = ""
        try:
            with open(path, "r") as f:
                js = f.read()
                js = js.replace(" ", "")
                js = js.replace("\n", "")
            for i in attrlist:
                fnd = '"'+graph.nodes[i[0]]['name']+'":'
                ind = js.find(fnd, lastind) + len(fnd) - 1
                if(js[ind+1]=='"'):
                    ind+=2
                    a = js.find('"', ind)
                    i.append(js[ind:a])
                    #attrlist[i][1] += js[ind:a]
                else:
                    ind+=1
                    a = js.find(',', ind)
                    b = js.find('}', ind)
                    if b < a: a = b
                    i.append(js[ind:a])
                    #attrlist[i][1] += js[ind-1:a]
                lastind = a
        except FileNotFoundError:
            print('Arquivo '+path+ ' não encontrado.')


        #except FileNotFoundError:
        #    print('Arquivo <'+path+'> nao encontrado.')
    #print('imprimindo attrlist \n')
    return attrlist


