import sys
import networkx as nx
from pylev import levenshtein
from pyjarowinkler import distance

def Pro(jstring, i, lvl, node_number, grafo):
    pro2_flag = 0
    return_dict = {}
    i = jstring.find('"properties":{"', i) + len('"properties":{"')
    j = 0
    tmp = ""
    while(True):
        node_base = node_number
        tmp = ""
        j = jstring.find('"', i)
        tmp += jstring[i:j]
        tmp_type = findtype(jstring, i)
        grafo.add_node(node_number, name=tmp, type=tmp_type, height=lvl)
        return_dict.update({node_number : [tmp, tmp_type, lvl]})
        node_number+=1

        if(tmp_type == 'array'):#1
            i = jstring.find('"items":{"') + len('"items":{"')#2
            tmp_type = findtype(jstring, i)# 3
            print(tmp_type)

            if(tmp_type == 'object'):
                print("abacateiro")
                i = jstring.find('"properties":{"', i,) + len('"properties":{"')#6
                print("abacate")
                while(True):
                    lvl += 1    #tratando dos elementos do vetor, entao a altura é maior
                    tmp = ""    #limpa o container do nome
                    j = jstring.find('"', i) #encontra o fim do nome
                    tmp += jstring[i:j] #recebe o nome do item
                    tmp_type = findtype(jstring, i) #recebe o tipo do item
                    grafo.add_node(node_number, name=tmp, type=tmp_type, height=lvl)#cria o nó
                    #return_dict.update({node_number : [tmp, tmp_type, lvl]}) acho q nao precisa?
                    node_number+=1 # incrementa o contador de nós

                    i = jstring.find('}', i) + 1

                    if(jstring[i+1] == ','):
                        i += 3
                        continue
                    elif(jstring[i+1] == '}'):
                        break
                lvl -= 1
            #else: 
            # i = jstring.find('}', i+1)            


            
        elif(tmp_type == 'object'):
            pro2_flag = 1
            retorno_t = Pro(jstring, i, lvl + 1, node_number, grafo)
            i = retorno_t[1]
            node_number = retorno_t[3]

            for key, value in retorno_t[0].items():
                if(value[2] == lvl+1):
                    grafo.add_edge(node_base, key)

            #for key, value in retorno_t[0]:
            #    d.add_edge(node_base, key)


        i = jstring.find('}', i+1)

        if(i+1 == len(jstring)):
            break
        elif(jstring[i+1] == ','):
            i += 3
            continue
        elif(jstring[i+1] == '}'):
            if(pro2_flag == 1):
                i += 2
            else:
                i+=1
            break
        else:
            break
    tupla_retorno = (return_dict, i, lvl, node_number, grafo)
    return tupla_retorno



def findtype(jstring, i):
    i = jstring.find('"type":"', i) + len('"type":"')
    j = jstring.find('"', i)
    return jstring[i:j]


def compJaroWink(graph1, graph2, node1, node2):
    return distance.get_jaro_distance(graph1.node[node1]['name'], graph2.node[node2]['name'], winkler=True, scaling=0.1)

def compLeven(graph1, graph2, node1, node2):
    return levenshtein(graph1.node[node1]['name'], graph2.node[node2]['name'])

def compGraphs(graph1, graph2, node_number1, node_number2):#todos os nos de x com todos os nos de y
    result = []
    for x in range(0, node_number1):
        for y in range(0, node_number2):
            result.append((graph1.node[x]['name'], graph2.node[y]['name'], (compJaroWink(graph1, graph2, x, y) + (1 - (compLeven(graph1, graph2, x, y)/max(len(graph1.node[x]['name']), len(graph2.node[y]['name'])))))/2))
    return result

if (__name__ == "__main__"):
    filenum = len(sys.argv)#holds the number of files entered + 1
    filename = [] #filename is a list that holds the file names
    for x in range(1, filenum):
        filename.append(sys.argv[x])

    jstring = ""

    graphs_dict = {} # holds the file name as key and graph as value
                     # the graph name will be the file name
    graphs_size = {}

    for x in range(0, filenum - 1):
        graphs_dict.update({filename[x]:nx.Graph()})
        graphs_size.update({filename[x]: 0})

    node_number = 0
    for x in range(0, filenum - 1):
        node_number = 0
        try:
            with open(filename[x], "r") as f:
                jstring = f.read()
            jstring = jstring.replace(" ", "")#TODO: 
            jstring = jstring.replace("\n", "")
            final = Pro(jstring, 0, 0, 0, graphs_dict.get(filename[x]))
            graphs_size.update({filename[x]:final[3]})
        except FileNotFoundError:
            print(f"Arquivo '{filename}' não encontrado.")#Ja criou o filename no dict, TODO: verificar se ele existe antes 

    if(filenum > 2):
        for x in range(0, filenum - 1):
            for y in range(x+1, filenum - 1):
                result = compGraphs(graphs_dict[filename[x]], graphs_dict[filename[y]], graphs_size[filename[x]], graphs_size[filename[y]])
                print(filename[x] + " X " + filename[y])
                for i in range(0, len(result)):
                    print(result[i])
                print("----------------------------")
    
    else:
        print("Apenas um arquivo foi recebido")
