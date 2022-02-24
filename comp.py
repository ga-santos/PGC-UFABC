import sin
import sem
import data
import os
import math

def compGraph(graph1, graph2, node_number1, node_number2, file1index, file2index, part):
        result = []
        tmp = []
        aux = []
        #print("Processo " + str(os.getpid())+ " iniciando.")

        totalIterations = node_number1 * node_number2

        if (part == 0):
                firstPosition = 0
                lastPosition = totalIterations
        else:
                totalPerPart = math.ceil(totalIterations / 5)

                firstPosition = (part - 1) * totalPerPart
                lastPosition = (part * totalPerPart) - 1

                print("Total", totalIterations, "PerPart", totalPerPart)

        count = 0
        for x in range(0, node_number1):
                for y in range(0, node_number2):
                        if(count >= firstPosition and count <= lastPosition):
                                #print("entrou posicao",count)
                                if graph1.nodes[x]['type'] == 'object' or graph2.nodes[y]['type'] == 'object':
                                        tmp.extend([graph1.nodes[x]['name'], None, None])
                                        tmp.extend([graph2.nodes[y]['name'], None, None])
                                        tmp.append(None)
                                        result.append(tmp)
                                        tmp = []
                                else:
                                        tmp.append(sin.compJaroWink(graph1, graph2, x, y))
                                        tmp.append(sem.wupSim(graph1, graph2, x, y))
                                        tmp.extend([data.compData(graph1, graph2, x, y)])
                                        aux.extend([graph1.nodes[x]['name'], graph1.nodes[x]['comp'], graph1.nodes[x]['orig']])
                                        aux.extend([graph2.nodes[y]['name'], graph2.nodes[y]['comp'], graph2.nodes[y]['orig']])
                                        aux.extend(tmp)
                                        result.append(aux)
                                        aux = []
                                        tmp = []
                        elif(count > lastPosition):
                                break

                        count += 1

        #print("Processo " + str(os.getpid())+ " terminou.")
        return [(file1index, file2index), result]



