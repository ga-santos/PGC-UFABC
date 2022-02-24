import networkx as nx


def Pro(jstring, i, lvl, node_number, grafo):#1
    return_dict = {}
    i = jstring.find('"properties":{"', i) + len('"properties":{"')#1.1
    j = 0
    tmp = ""
    while(True):
        node_base = node_number
        tmp = ""
        j = jstring.find('"', i)
        tmp += jstring[i:j]#1.2
        aux = findtype(jstring, i)
        tmp_type = aux[0]
        j = aux[1]
        i = j
        grafo.add_node(node_number, name=tmp, type=tmp_type, height=lvl)
        return_dict.update({node_number : [tmp, tmp_type, lvl]})#Necessario ainda?
        node_number+=1

        if(tmp_type == 'array'):#4
            i = jstring.find('"items":{', i) + len('"items":{')#4
            tmp_type = findtype(jstring, i)[0]#ja encontra o tipo
            if(tmp_type == 'object'):
                i = jstring.find('"properties":{"', i) + len('"properties":{"')#6
                array_edge = node_number - 1 
                lvl += 1
                while(True):
                    tmp = ""    #limpa o container do nome
                    j = jstring.find('"', i) #encontra o fim do nome
                    tmp += jstring[i:j] #recebe o nome do item
                    tmp_type = findtype(jstring, i)[0] #recebe o tipo do item
                    grafo.add_node(node_number, name=tmp, type=tmp_type, height=lvl)#cria o nó
                    grafo.add_edge(array_edge, node_number)
                    #return_dict.update({node_number : [tmp, tmp_type, lvl]}) acho q nao precisa?
                    node_number+=1 # incrementa o contador de nós

                    i = jstring.find('}', i)

                    if(jstring[i+1] == ','):#teoricamente tratando corretamente
                        i += 3
                        continue
                    elif(jstring[i+1] == '}'):
                        i+=1
                        i = jstring.find('}', i+1)
                        break
                lvl -= 1
            else: 
                i = jstring.find('}', i)



            
        elif(tmp_type == 'object'):#3
            retorno_t = Pro(jstring, i, lvl + 1, node_number, grafo)
            i = retorno_t[1]
            node_number = retorno_t[3]

            for key, value in retorno_t[0].items():
                if(value[2] == lvl+1):
                    grafo.add_edge(node_base, key)
                    #print(value)


        if(jstring[i]== '}'):
            i = jstring.find('}', i+1)
        else:
            i = jstring.find('}', i)

        if(i+1 == len(jstring)):#verificar se está chegando nesse caso
            break
        elif(jstring[i+1] == ','):
            i += 3#.find('"', i)
            continue
        elif(jstring[i+1] == '}'):
            i += 1
            break
        else:
            break
    tupla_retorno = (return_dict, i, lvl, node_number, grafo)
    return tupla_retorno



def findtype(jstring, i):
    i = jstring.find('"type":"', i) + len('"type":"')
    j = jstring.find('"', i)
    return (jstring[i:j], j)
