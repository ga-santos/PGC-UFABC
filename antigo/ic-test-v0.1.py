import sys
import networkx as nx
from pyjarowinkler import distance

def Pro(jstring, i, lvl, node_number):
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
        d.add_node(node_number, name=tmp, type=tmp_type, height=lvl)
        return_dict.update({node_number : [tmp, tmp_type, lvl]})
        node_number+=1

        if(tmp_type == 'array'):#1
            print("array type iniciado")
            i = jstring.find('"items":{"') + len('"items":{"')#2
            tmp_type = findtype(jstring, i)# 3
            print(tmp_type)

            if(tmp_type == 'object'):
                i = jstring.find('"properties":{"', i,) + len('"properties":{"')#6
                while(True):
                    lvl += 1#tratando dos elementos do vetor, entao a altura é maior
                    tmp = ""
                    j = jstring.find('"', i)
                    tmp += jstring[i:j]
                    tmp_type = findtype(jstring, i)
                    d.add_node(node_number, name=tmp, type=tmp_type, height=lvl)
                    return_dict.update({node_number : [tmp, tmp_type, lvl]})
                    node_number+=1

                    i = jstring.find('}', i)
                    print(i, jstring[i:i+3])

                    if(jstring[i+1] == ','):
                        i += 3
                        continue
                    elif(jstring[i+1] == '}'):
                        break
            else: 
                i = jstring.find('}', i+1)


            
        elif(tmp_type == 'object'):
            pro2_flag = 1
            retorno_t = Pro(jstring, i, lvl + 1, node_number)
            for key, value in retorno_t[0].items():
                print(key, value[0], value[1], value[2])
            
            i = retorno_t[1]
            node_number = retorno_t[3]

            for key, value in retorno_t[0].items():
                if(value[2] == lvl+1):
                    d.add_edge(node_base, key)

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
    tupla_retorno = (return_dict, i, lvl, node_number)
    return tupla_retorno



def findtype(jstring, i):
    i = jstring.find('"type":"', i) + len('"type":"')
    j = jstring.find('"', i)
    return jstring[i:j]


def compJaroWink(d1, d2, node1, node2):
    return distance.get_jaro_distance(d1.node[node1]['name'], d2.node[node2]['name'], winkler=True, scaling=0.1)

def compGraphs(d1, d2, node_number1, node_number2, x):
    results_list = []
    for x in range(0, node_number1):
        for y in range(0, node_number2):
            results_list.append(f"{d1.node[x]['name']} {d2.node[y]['name']} " + compJaroWink(d1, d2, x, y))
    return results_list

if (__name__ == "__main__"):
    filename = sys.argv[1]
    jstring = ""
    try:
        with open(filename, "r") as f:
            jstring = f.read()
        jstring = jstring.replace(" ", "")
        jstring = jstring.replace("\n", "")
        d = nx.DiGraph()
        node_number = 0
        final = Pro(jstring, 0, 0, 0)
        node_number = final[3]

        #for x in range(0, node_number):
        #   print(f" {d.node[x]['name']} {d.node[x]['type']} {d.node[x]['height']} {compJaroWink(d, x, x)}")
        
        for x in  d.edges():
            print(f"{x}")
        
        for x in range(0, node_number):
            print(f"{d.node[x]['name']}")

    except FileNotFoundError:
        print(f"Arquivo '{filename}' não encontrado.")