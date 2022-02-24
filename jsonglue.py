import sys
import networkx as nx
import comp as cp
import grafo as gr
import time
import os.path
import sem
import jsongenerator as jg
import multiprocessing as mp
import data as dt
from colorama import Fore, Back, Style
import re  # regular expression
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from functools import partial


def loadNamingStd ():
    d_Names = {}

    with open("NamingStandards.txt") as f:
        for line in f:
            (val, key) = line.split()
            d_Names[key] = val
    return d_Names

def cleanString(in_str):
    if not isinstance(in_str, str):
        return None
    # Remove Special Char, Number....
    clean_str = re.sub('[^A-Za-z]+', ' ', in_str.lower())
    # Remove additional space between words
    clean_str = re.sub(' +',' ',clean_str)
    # Extract Stop words
    stop_words = set(stopwords.words('english')) 
    # Extract Stop words
    tokens = word_tokenize(clean_str)
    str_list = [w for w in tokens if not w in stop_words]
    return ' '.join(map(str, str_list))


def removeSpaces(js):
    ret = ''
    f = 1
    for i in js:
        if ((i == ' ' or i == '\n') and f == 1): continue
        elif(i == '"'):
            ret += i
            f *= -1
        else: ret +=i
    return ret
    

def formatName(name):
    a = name.rfind('/')
    b = name.rfind('.')
    return name[a+1:b]

def formatName2(name):
    a = name.rfind('/')
    return name[a+1:]

def everyName(filename, x, graphs_dict, graphs_size, graphs_names):
    g = graphs_dict[filename[x]] # The wanted graph
    size = graphs_size[filename[x]] # The graph's size
    namelist = []
    for i in range(0, size):
        namelist.append(g.node[i]['name']) # For every node, take it's name
    graphs_names.update({filename[x]:namelist})

def printResults(full):
    print('\n')
    for filecomp in full:
        print("             ==================        Schema " + Back.BLACK + Fore.WHITE + filecomp[0] + Style.RESET_ALL + ' vs Schema ' + Back.BLACK + Fore.WHITE + filecomp[1] + Style.RESET_ALL + '       ==================\n' )
        #print("========        Schema " + filecomp[0] + ' vs Schema ' + filecomp[1] + '       ========\n')
        count = 0
        for comparison in filecomp[2]:
            Sin = comparison[6] 
            x = comparison[6:len(comparison)]
            z = 0
            el = 10
            for a in x:
                z = z + 1
                if z == 2: Sem  = a
                if z == 3: Hist = a[2]

            if Sin is None or Sem is None or Hist is None: continue
            if float (Sin) <= 0.2 or float(Sem) <= 0.2 or float(Hist) <= 3.5:
                printAux(comparison)
                print("             ", end="")
                print(comparison[:3], end='')
                print('      -      ', end='')
                print(comparison[3:6], '\n')
                print("            ", comparison[6:len(comparison)])
                print(Sin, Sem, Hist)
                print('\n')
                count = count + 1
        print('\n\n')
        print ("temos...", count)
        print("Press the <ENTER> key to continue...")
        input()


def printAux(comparison):
    print('               Form' + (' '*(len(comparison[0]))), end='')
    print('Sem'+ (' '*(len(str(comparison[1]))+1)), end='')
    print('Orig' + (' '*(len(str(comparison[2]))+13)), end='')
    print('Form' + (' '*(len(comparison[3]))), end='')
    print('Sem'+ (' '*(len(str(comparison[4]))+1)), end='')
    print('Orig')

def createRandomJSON1(qnt): # Creates 'qnt' JSON files in documents/ folder 
    if os.path.isdir('documents') == False: os.system('mkdir documents')
    pth = 'documents/caso1-file.json'
    if os.path.isfile(pth) == True: os.system('rm '+pth)
    try:
        with open(pth, "w") as f:
            f.write(jg.createDoc1(qnt))
    except:
        print('Erro ao salvar documento JSON em '+ pth + ' .')
        raise


def createRandomJSON2(qnt): # Creates 'qnt' JSON files in documents/ folder 
    if os.path.isdir('documents') == False: os.system('mkdir documents')
    pth = 'documents/caso2-file.json'
    if os.path.isfile(pth) == True: os.system('rm '+pth)
    try:
        with open(pth, "w") as f:
            f.write(jg.createDoc2(qnt))
    except:
        print('Erro ao salvar documento JSON em '+ pth + ' .')
        raise

def createRandomJSON3(qnt): # Creates 'qnt' JSON files in documents/ folder 
    if os.path.isdir('documents') == False: os.system('mkdir documents')
    pth = 'documents/caso3-file.json'
    if os.path.isfile(pth) == True: os.system('rm '+pth)
    try:
        with open(pth, "w") as f:
            f.write(jg.createDoc3(qnt))
    except:
        print('Erro ao salvar documento JSON em '+ pth + ' .')
        raise
    
def formatTime(t):
    s = t%60
    t = t/60
    m = t%60
    t = t/60
    h = t
    return "{:02d}".format(int(h))+'h'+"{:02d}".format(int(m))+'m'+"{:02d}".format(int(s))+'s'

def auxMultipro(a, x, y):
        b = dt.returnDataList(a, x, y)
        c = dt.returnAver(b)
        d = dt.buildHist(c)
        e = dt.normData(d)
        return e

if (__name__ == "__main__"):
    start = time.time()

    arguments = sys.argv
    flags = []
    for arg in arguments:
        if arg[0] == '-':
            flags.append(arg)

    for f in flags:
        if f in arguments:
            arguments.remove(f)
    
    filenum = len(arguments)#holds the number of files entered + 1
    filename = [] #filename is a list that holds the file names

    #if argv is a file, appends it to the filename list
    #if not decreases filenum variable
    for x in range(1, filenum):
        if(os.path.isfile(arguments[x])):
            filename.append(arguments[x])
        else:
            filenum = filenum - 1

    jstring = ""

    graphs_dict = {} # holds the file name as key and graph as value,  the graph name will be the file name
    graphs_size = {}

    graphs_names = {} # holds every name of every schema


    for x in range(0, filenum - 1):
        graphs_dict.update({filename[x]:nx.Graph()})
        graphs_size.update({filename[x]: 0})

    node_number = 0
    for x in range(0, filenum - 1):
        node_number = 0
        try:
            with open(filename[x], "r") as f:
                jstring = f.read()
            jstring = removeSpaces(jstring)
            final = gr.Pro(jstring, 0, 0, 0, graphs_dict.get(filename[x]))
            graphs_size.update({filename[x]:final[3]})
        except FileNotFoundError:   #Ja foi verificado, mas vale deixar aqui ainda
            print("Arquivo %s não encontrado." % filename[x])#Ja criou o filename no dict


    if '-r' in flags:
        createRandomJSON1(1000)
        createRandomJSON2(1000)
        createRandomJSON3(1000)
        sys.exit()

    std = loadNamingStd()

    if '-m' in flags:
        cores = mp.cpu_count()
        files = len(filename)
        if files > cores:pool1 = mp.Pool(cores)
        else:            pool1 = mp.Pool(files)

        print('Leitura multiprocessada iniciada.')

        for i in filename:
            x = partial(dt.applyData2Graph, graph=graphs_dict[i], nodes=graphs_size[i])
            pool1.apply_async(auxMultipro, args=(i, graphs_dict[i], graphs_size[i]), callback=x)

        pool1.close()
        pool1.join()

        print('Leitura multiprocessada encerrada.')

    else:
        print('Leitura sequencial iniciada.')
        for i in filename:
            print('Arquivo', i, 'iniciado.')
            a = dt.returnDataList(i, graphs_dict[i], graphs_size[i])
            if a == None: dt.applyData2Graph(a, graphs_dict[i], graphs_size[i])
            else:
                b = dt.returnAver(a)
                c = dt.buildHist(b)
                d = dt.normData(c)
                dt.applyData2Graph(d, graphs_dict[i], graphs_size[i])
            print('Arquivo', i, 'encerrado.')
        print('Leitura sequencial encerrada')

    for i in filename:
        k = graphs_size[i]
        for j in range(0, k):
            graphs_dict[i].nodes[j]['orig'] = graphs_dict[i].nodes[j]['name']
            tmp = cleanString(graphs_dict[i].nodes[j]['name'])
            #graphs_dict[i].nodes[j]['name'] = cleanString(graphs_dict[i].nodes[j]['name'])
            names = tmp.split()
            for x in range(0, len(names)):
                new = std.get(names[x])
                if new == None:
                    continue
                else:
                    names[x] = new
            graphs_dict[i].nodes[j]['name'] = ' '.join(names)
            


    full = []
    header = []
    comp = []

    if(filenum == 1):
        print("Não foi passado nenhum arquivo ou os arquivos não existem.")
    elif(filenum > 2):
        print('\nComparação de schemas iniciada.')
        if '-m' in flags:
            pool = mp.Pool(mp.cpu_count())
            schemacomb = []
            for x in range(0, filenum - 1):
                for y in range(x+1, filenum - 1):
                    schemacomb.append((x, y))
            comp = [pool.apply_async(cp.compGraph, args=(graphs_dict[filename[x]], graphs_dict[filename[y]], graphs_size[filename[x]], graphs_size[filename[y]], x, y)) for (x, y) in schemacomb]
            comp = [r.get() for r in comp]
            pool.close()
            pool.join()

            for i in comp: # TODO reescrever usando formatName
                file1 = filename[i[0][0]]
                file2 = filename[i[0][1]]
                a1 = file1.rfind('/', 0)
                a2 = file2.rfind('/', 0)
                if a1 == -1:
                    header.append(file1)
                else: header.append(file1[a1+1:len(file1)])
                if a2 == -1:
                    header.append(file2)
                else: header.append(file2[a2+1:len(file2)])
                header.append(i[1])
                full.append(header)
                header = []
        else:
            for x in range(0, filenum - 1):
                for y in range(x+1, filenum - 1):
                    header.append(formatName(filename[x]))
                    header.append(formatName(filename[y]))
                    comp = cp.compGraph(graphs_dict[filename[x]], graphs_dict[filename[y]], graphs_size[filename[x]], graphs_size[filename[y]], x, y)
                    header.append(comp[1])
                    full.append(header)
                    header = []
    else:
        print("Apenas um arquivo foi recebido")


    #print("Printando dados\n")
    #[print(i, end='\n\n') for i in dt.returnDataList(filename[0], graphs_dict[filename[0]], graphs_size[filename[0]])]

    end = time.time()

    printResults(full)
    if '-m' in flags:print("Time multiprocess : "+ formatTime(end - start))
    else:            print("Time sequential : " + formatTime(end - start))
    

