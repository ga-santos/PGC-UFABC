import ast
import os
import signal
import random
import dash
import numpy as np
import jsonglue_dash as jg
import dash_cytoscape as cyto
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

posicaoListaCombinacoes = 0
posicaoRegistro = 0
listaCombinacoes = []

parte = 1
dadosComparacaoJSONGlue = []

dictListaNodes1 = {}
dictListaNodes2 = {}
invDictListaNodesTotal = {}

arestasAtuais = []
nodesAtuais = []
registroArestas = []
registroNodes = []
ultimoIdArestas = 0

dadosReduzidoComparacaoJSONGlue = []

paresConfirmados = []
paresRecusados = []

arestaSelecionada = []

inputSchemas = ""

inputs = [["inputValorFiltro","value"], ["btCarregarAnterior","n_clicks"], ["btCarregarInicio","n_clicks"], ["btCarregarProximo","n_clicks"], ["btRecusarCorresp", "n_clicks"], ["btConfirmarCorresp", "n_clicks"], ["dropdownFiltros","value"]]

optionsDropdownFiltro = [
                            {'label': 'Diferença Média de Comprimento', 'value': 'DifMediaComp'},
                            {'label': 'Diferença Desvio Padrão dos dados', 'value': 'DifDesvioPadrao'}
                        ]

filtroAtivo = ""

def resetarVariveisGlobais():
    global posicaoListaCombinacoes
    global posicaoRegistro
    global listaCombinacoes
    global parte
    global dadosComparacaoJSONGlue
    global dictListaNodes1
    global dictListaNodes2
    global invDictListaNodesTotal
    global arestasAtuais
    global nodesAtuais
    global registroArestas
    global registroNodes
    global ultimoIdArestas
    global dadosReduzidoComparacaoJSONGlue
    global paresConfirmados
    global paresRecusados
    global arestaSelecionada
    global filtroAtivo

    posicaoListaCombinacoes = 0
    posicaoRegistro = 0
    listaCombinacoes = []

    parte = 1
    dadosComparacaoJSONGlue = []

    dictListaNodes1 = {}
    dictListaNodes2 = {}
    invDictListaNodesTotal = {}

    arestasAtuais = []
    nodesAtuais = []
    registroArestas = []
    registroNodes = []
    ultimoIdArestas = 0

    dadosReduzidoComparacaoJSONGlue = []

    paresConfirmados = []
    paresRecusados = []

    arestaSelecionada = []

    filtroAtivo = ""

def obterNomesSchemas():
    tupla = listaCombinacoes[posicaoListaCombinacoes]
    nomesSchemas = jg.obterNomesSchemas(tupla[0], tupla[1])
    return [str(nomesSchemas[0]),str(nomesSchemas[1])]


"""
OBJETIVO: Executar JSONGlue transformando as entradas em grafos. Obter acesso a lista de combinações de comparações.
"""
def carregaJsonGlue():
    global listaCombinacoes
    global inputSchemas

    esquemas = ""
    #jg.leituraSchemas("covidA.json covidB.json")
    #jg.leituraSchemas("caso1.json caso2.json caso3.json")

    countWords = 0
    for esquema in inputSchemas.split(" "):
        esquemas += esquema + ".json"

        countWords += 1
        if countWords != len(inputSchemas.split(" ")):
            esquemas += " "

    jg.leituraSchemas(esquemas)

    listaCombinacoes = jg.combinacoesSchemas

"""
OBJETIVO: A partir da tupla com os schemas para comparação na posição atual é feita a comparação via JSONGlue e os dados são retornados para uso no Dash.
"""
def compararSchema(parte):
    global dadosComparacaoJSONGlue
    global listaCombinacoes
    global posicaoListaCombinacoes

    dadosComparacaoJSONGlue = []
    tupla = listaCombinacoes[posicaoListaCombinacoes]
    comparacao = jg.compararSchemas(tupla[0], tupla[1], parte)

    comparacaoTratada = [elem for elem in comparacao[0][2] if len(elem) > 7]
    comparacao[0][2] = comparacaoTratada
    dadosBrutos = comparacao[0][2]

    for dado in dadosBrutos:
        if (dado[8][0] != None):
            dadosComparacaoJSONGlue.append(dado)

    listaElementos = carregarGrafoCytoscape()
    
    return listaElementos

"""
OBJETIVO: A partir do retorno do JSONGlue faz a criação da lista utilizada para inserção dos dados no Cytoscape
"""
def carregarGrafoCytoscape():
    global dadosComparacaoJSONGlue
    global dictListaNodes1
    global dictListaNodes2
    global invDictListaNodesTotal
    global arestasAtuais
    global nodesAtuais
    global ultimoIdArestas

    listaNodes1 = []
    listaNodes2 = []

    #clusters = prepararKmeans(dadosComparacaoJSONGlue)

    # ---------------------- Para cada schema separa o nome dos elementos únicos ---------------------- #
    for i, row in enumerate(dadosComparacaoJSONGlue):
        nomeElemento1 = row[0]
        nomeElemento2 = row[3]
        listaNodes1.append(nomeElemento1)
        listaNodes2.append(nomeElemento2)

    listaNodes1 = list(dict.fromkeys(listaNodes1))
    listaNodes2 = list(dict.fromkeys(listaNodes2))
    listaNodesTotal = list(dict.fromkeys(listaNodes1 + listaNodes2))

    # ---------------------- Cria um dicionário com uma chave para cada elemento único do schema ---------------------- #
    dictListaNodes1 = {}
    for i, node in enumerate(listaNodes1):
        dictListaNodes1[node] = i

    dictListaNodes2 = {}
    for i, node in enumerate(listaNodes2):
        dictListaNodes2[node] = i + len(listaNodes1)

    # ---------------------- A partir do mesmo dicionário cria outro dicionário invertendo a chave ---------------------- #
    invDictListaNodes1 = {dictListaNodes1[k] : k for k in dictListaNodes1}
    invDictListaNodes2 = {dictListaNodes2[k] : k for k in dictListaNodes2}
    invDictListaNodesTotal = {**invDictListaNodes1, **invDictListaNodes2}

    # ---------------------- Gera a lista de nós no formato JSON para o Cytoscape ---------------------- #
    jsonListaNodes1 = gerarNodes(listaNodes1,1,0)
    jsonListaNodes2 = gerarNodes(listaNodes2,2,len(dictListaNodes1))
    nodesAtuais = jsonListaNodes1 + jsonListaNodes2

    if ultimoIdArestas == 0:
        ultimoIdArestas = len(nodesAtuais)

    # ---------------------- Salva os dados das arestas que foram geradas ---------------------- #
    arestasAtuais = gerarArestas(dadosComparacaoJSONGlue) #, len(invDictListaNodesTotal) + (len(arestasAtuais)  * (parte - 1))

    listaElementos = nodesAtuais + arestasAtuais

    return listaElementos


def gerarNodes(listaNodes,classes,firstId):
    return [
        {
            "data": {
                "id": str(firstId + i),
                "label": node,
                "title": node,
                "node_size": 10,
            },
            "position": {
                "x": i*65 + random.randint(100,600) #random.randint(1,100)*i
                ,"y": classes*150 + random.randint(100,600)
            },
            "classes": str(classes),
            "selectable": True
        }
        for i, node in enumerate(listaNodes)
    ]

def gerarArestas(data):
    global dictListaNodes1
    global dictListaNodes2
    global ultimoIdArestas

    listaArestas = list()

    for i, row in enumerate(data):
        v1 = row[0]
        v2 = row[3]

        temp_dict = {
            "data": {
                        "id": ultimoIdArestas + i,
                        "source": dictListaNodes1[v1],
                        "target": dictListaNodes2[v2],
                        "media_comprimento": row[6],
                        "desvio_padrao": row[7],
                        "histograma": row[8],
                     },
            "classes": "1",
            "locked": True,
        }

        listaArestas.append(temp_dict)

    ultimoIdArestas = listaArestas[-1]["data"]["id"] + 1
    return listaArestas


# -------------------------------------------- GRAFO REDUZIDO -------------------------------------------- #
def compararTodosSchemasReduzido():
    global dadosReduzidoComparacaoJSONGlue
    global listaCombinacoes

    for tupla in listaCombinacoes:
        comparacao = jg.compararSchemas(tupla[0], tupla[1], 0)
        comparacaoTratada = [elem for elem in comparacao[0][2] if len(elem) > 7]
        dadosComparacaoJSONGlue = comparacaoTratada

        qtd_dados = 0
        media_comprimento = 0
        desvio_padrao = 0

        hist0 = 0
        hist1 = 0
        hist2 = 0
        for comp in dadosComparacaoJSONGlue:
            if (comp[8][0] != None):
                qtd_dados += 1
                media_comprimento += float(comp[6])
                desvio_padrao += float(comp[7])
                hist0 += float(comp[8][0])
                hist1 += float(comp[8][1])
                hist2 += float(comp[8][2])


        media_media_comprimento = media_comprimento / qtd_dados
        media_desvio_padrao = desvio_padrao / qtd_dados
        media_hist0 = hist0 / qtd_dados
        media_hist1 = hist1 / qtd_dados
        media_hist2 = hist2 / qtd_dados

        dadosReduzidoComparacaoJSONGlue.append([comparacao[0][0], comparacao[0][1], str(media_media_comprimento), str(media_desvio_padrao), [str(media_hist0), str(media_hist1), str(media_hist2)]])

    listaElementos = carregarGrafoReduzidoCytoscape()

    return listaElementos

def carregarGrafoReduzidoCytoscape():
    global dadosReduzidoComparacaoJSONGlue
    global invDictListaNodesTotal

    listaNodes1 = []
    listaNodes2 = []

    for i, row in enumerate(dadosReduzidoComparacaoJSONGlue):
        v1 = row[0]
        v2 = row[1]
        listaNodes1.append(v1)
        listaNodes2.append(v2)

    listaNodes1 = list(dict.fromkeys(listaNodes1))
    listaNodes2 = list(dict.fromkeys(listaNodes2))
    listaNodesTotal = list(dict.fromkeys(listaNodes1 + listaNodes2))

    dictNumNodeReduzido = {}
    for i, node in enumerate(listaNodesTotal):
        dictNumNodeReduzido[node] = i

    invDictListaNodesTotal = {dictNumNodeReduzido[k] : k for k in dictNumNodeReduzido}

    nodesAtuais = gerarNodesReduzido(listaNodesTotal,0)
    arestasAtuais = gerarArestasReduzido(dadosReduzidoComparacaoJSONGlue, dictNumNodeReduzido)

    listaElementos = nodesAtuais + arestasAtuais

    return listaElementos

def gerarNodesReduzido(lista,firstId):
    return [
        {
            "data": {
                "id": str(firstId + i),
                "label": node,
                "title": node,
                "node_size": 10,
            },
            "position": {
                "x": i*65 + random.randint(100,300) #random.randint(1,100)*i
                ,"y": (firstId + i)*150 + random.randint(100,300)
            },
            "classes": str(firstId + i),
            "selectable": True
        }
        for i, node in enumerate(lista)
    ]


def gerarArestasReduzido(data, dictNumNodeReduzido):
    global ultimoIdArestas

    listaArestas = list()

    for i, row in enumerate(data):
        v1 = row[0]
        v2 = row[1]

        temp_dict = {
            "data": {
                "id": ultimoIdArestas + i,
                "source": dictNumNodeReduzido[v1],
                "target": dictNumNodeReduzido[v2],
                "media_comprimento": row[2],
                "desvio_padrao": row[3],
                "histograma": row[4],
            },
            "classes": "1",
            "locked": True,
        }

        listaArestas.append(temp_dict)

    ultimoIdArestas = listaArestas[-1]["data"]["id"] + 1
    return listaArestas

"""
def carregaDados(grafoJsonGlue):
    global dadosComparacaoJSONGlue
    #f = open("saida.txt","r")
    #var = f.read()
    #f.close()
    #var = ast.literal_eval(grafoJsonGlue)

    dadosComparacaoJSONGlue = grafoJsonGlue[0][2]
    #print(dadosComparacaoJSONGlue)
"""

StartupListaElementosCyto = []
listaElementosCyto = StartupListaElementosCyto

default_media = 1
titulo = ""

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
body_layout = html.Div(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Form(
                        [
                            dcc.Input(
                                id="input_schemas",
                                placeholder = 'Digite os schemas',
                                type = 'text',
                                style = {"border-radius": "4px"}
                            )
                        ]
                    )
                ),

                dbc.Col([dbc.Button("Iniciar Correspondências", color="primary", id="btCarregarInicio", n_clicks=0, size="sm")]),
                dbc.Col([dbc.Button("Próximo Matching", color="outline-primary", id="btCarregarProximo", n_clicks=0, size="sm")], style = {"margin-left": "-3%"}),
                dbc.Col([dbc.Button("Matching Anterior", color="outline-primary", id="btCarregarAnterior", n_clicks=0, size="sm")], style = {"margin-left": "-6%"}),

                dbc.Col(
                    [dbc.Badge(
                        "Filtros", className="mr-1", style={"font-size": "medium"}
                    )]
                ),
                dbc.Col(
                        dcc.Dropdown(
                            options=optionsDropdownFiltro,
                            id="dropdownFiltros",
                            placeholder="Selecione um filtro.."
                        ),
                        style={"margin-left": "-10%"}
                ),
                dbc.Col(
                    dbc.Form(
                        [
                            dcc.Input(
                                id="inputValorFiltro",
                                placeholder = 'Digite um valor...',
                                type = 'number',
                                value = default_media,
                                style={"width": "40%", "border-radius": "4px"}
                            )
                        ]
                    )
                )
            ]
        ),
        dbc.Row(
                html.H5(titulo, id="titulo_H5", style={'textAlign': 'center', 'margin-top': '1%'})
        ),
        dbc.Row(
            [
                cyto.Cytoscape(
                    id="core_19_cytoscape",
                    layout={"name": "preset"},
                    style={"width": "100%", "height": "550px"},
                    elements=StartupListaElementosCyto,
                    minZoom=0.65,
                    maxZoom=0.95,
                    zoom=1,
                    stylesheet=[
                        {
                            'selector': 'node',
                            'style': {
                                'label': 'data(label)'
                            }
                        },
                        {
                            'selector': '.1',
                            'style': {
                                'background-color': 'blue'
                            }
                        },
                        {
                            'selector': '.2',
                            'style': {
                                'background-color': 'red'
                            }
                        },
                        {
                            'selector': '.confirmado',
                            'style': {
                                'line-color': 'green'
                            }
                        },
                        {
                            'selector': '.recusado',
                            'style': {
                                'line-color': 'red'
                            }
                        },
                        {
                            'selector': '.ocultar',
                            'style': {
                                "visibility": "hidden"
                            }
                        }
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Alert(
                        id="edge-data",
                        children="Detalhes da correspondência dos elementos",
                        color="secondary",
                    )
                ),
                dbc.Col(
                    [
                        dbc.Button("Confirmar Correspondência", color="success", id="btConfirmarCorresp", n_clicks=0,
                               size="sm", style={"margin-right": "3%"}),
                        dbc.Button("Recusar Correspondência", color="danger", id="btRecusarCorresp", n_clicks=0,
                            size="sm")
                    ]
                )
            ],
        ),
        html.Br(),
        html.Div(id="output_schemas", style={"display": "none"})

    ], style={"margin-left": "5%", "margin-right": "5%"}
)

app.layout = html.Div([body_layout])



@app.callback(
    Output("output_schemas", "children"), Input("input_schemas", "value")
)
def salvarInputSchemas(value):
    global inputSchemas

    inputSchemas = value

    return value


"""
OBJETIVO: Ao clicar na aresta executa os comandos.
"""
@app.callback(
    Output("edge-data", "children"), Input("core_19_cytoscape", "selectedEdgeData")
)
def cliqueAresta(edge):
    global arestaSelecionada

    contents = []
    contents.append(html.H6("Detalhes da correspondência selecionada"))

    if edge is not None:
        if(len(edge) > 0):
            data = edge[0]
            arestaSelecionada = data
            #data['target'].connectedEdges().style({'line-color': 'red'})

            contents.append(html.Br())

            if posicaoListaCombinacoes < len(listaCombinacoes):
                nomesSchemas = obterNomesSchemas()


                #contents.append(html.H5("Title: " + data["id"].title()))
                contents.append(
                    html.H6(
                        "Elemento do esquema " + nomesSchemas[0] + ": " + invDictListaNodesTotal[int(data["source"])]
                    )
                )
                contents.append(
                    html.H6(
                         "Elemento do esquema " + nomesSchemas[1] + ": " + invDictListaNodesTotal[int(data["target"])]
                    )
                )

            contents.append(
                html.P(
                    "Diferença na média dos comprimentos dos dados (AVG): " + str(round(float(data['media_comprimento']),3))
                )
            )
            contents.append(
                html.P(
                    "Diferença no desvio padrão dos dados (STD): " + str(round(float(data['desvio_padrao']),3))
                )
            )
            contents.append(
                html.P(
                    "Análise histograma: " + ", ".join([str(round(float(x),3)) for x in data['histograma']])
                )
            )

    return contents


"""
OBJETIVO: Ao clicar no node executa os comandos.
"""
@app.callback(
    Output("node-data", "children"), [Input("core_19_cytoscape", "selectedNodeData")]
)
def cliqueNode(datalist):
    contents = []
    contents.append(html.H6("Detalhes do elemento selecionado"))

    if datalist is not None:
        if len(datalist) > 0:
            data = datalist[-1]

            contents.append(html.Br())
            #contents.append(html.H5("Title: " + data["label"].title()))
            contents.append(
                html.P(
                    "Id: "
                    + data["id"].title()
                )
            )
    return contents


"""
OBJETIVO: Executa uma ação para cada botão que é pressionado.
"""
@app.callback(
    [
        Output("core_19_cytoscape", "elements"),
        Output("titulo_H5", "children")
    ],
    [

        Input('{}'.format(input[0]), '{}'.format(input[1])) for input in inputs
    ],
)
def acoesInputs(inputValorFiltro, btCarregarAnterior, btCarregarInicio, btCarregarProximo, btConfirmarCorresp, btRecusarCorresp,dropdownFiltros):
    global listaElementosCyto
    global posicaoListaCombinacoes
    global posicaoRegistro
    global parte
    global filtroAtivo
    global arestasAtuais
    global nodesAtuais

    ctx = dash.callback_context
    input = ctx.triggered[0]['prop_id'].split('.')[0]

    titulo = ""

    if input == "btCarregarInicio":
        resetarVariveisGlobais()
        jg.resetarVariveisGlobais()
        carregaJsonGlue()
        posicaoListaCombinacoes = 0

        listaElementosCyto = compararSchema(parte=1)

    elif input == "btCarregarProximo": # COLOCAR TRAVA!
        parte += 1

        # Cadastramento de um novo registro (1ª vez que passou nesse conjunto)
        if len(registroArestas) < (posicaoRegistro + 1):
            registroArestas.append(arestasAtuais)
            registroNodes.append(nodesAtuais)

            # Verifica se a próxima parte avança para uma nova combinação
            if (parte > 5):
                parte = 1
                posicaoListaCombinacoes += 1

            if (posicaoListaCombinacoes < len(listaCombinacoes)):
                listaElementosCyto = compararSchema(parte)

            elif (posicaoListaCombinacoes == len(listaCombinacoes)):
                listaElementosCyto = compararTodosSchemasReduzido()

        # Está num conjunto que é o último conjunto que já foi registrado
        elif len(registroArestas) == (posicaoRegistro + 1):
            registroArestas[posicaoRegistro] = arestasAtuais
            registroNodes[posicaoRegistro] = nodesAtuais

            # Verifica se a próxima parte avança para uma nova combinação
            if (parte > 5):
                parte = 1
                posicaoListaCombinacoes += 1

            if (posicaoListaCombinacoes < len(listaCombinacoes)):
                listaElementosCyto = compararSchema(parte)
            elif (posicaoListaCombinacoes == len(listaCombinacoes)):
                listaElementosCyto = compararTodosSchemasReduzido()

        else: #Está num conjunto que está no meio da lista de registros

            # Verifica se a próxima parte avança para uma nova combinação
            if (parte > 5):
                parte = 1
                posicaoListaCombinacoes += 1

            #Salva os nós e arestas que estavam sendo editadas pelo usuário
            registroArestas[posicaoRegistro] = arestasAtuais
            registroNodes[posicaoRegistro] = nodesAtuais

            #Avança para o próximo conjunto de nós e arestas que já foi passado
            arestasAtuais = registroArestas[posicaoRegistro + 1]
            nodesAtuais = registroNodes[posicaoRegistro + 1]

            listaElementosCyto = nodesAtuais + arestasAtuais

        posicaoRegistro += 1

    elif input == "btCarregarAnterior":

        posicaoCheck = posicaoListaCombinacoes

        if (parte != 1):
            parte -= 1

        elif (parte == 1 and posicaoListaCombinacoes != 0):
            parte = 5
            posicaoListaCombinacoes -= 1

        if (len(registroArestas) == posicaoRegistro) and posicaoCheck != len(listaCombinacoes):
            registroArestas.append(arestasAtuais)
            registroNodes.append(nodesAtuais)

            """
            if posicaoListaCombinacoes == 0:
                if posicaoListaCombinacoes != len(listaCombinacoes):
                    registroArestas.append(arestasAtuais)
                    registroNodes.append(nodesAtuais)
            else:
                if (posicaoListaCombinacoes + 1) != len(listaCombinacoes):
                    registroArestas.append(arestasAtuais)
                    registroNodes.append(nodesAtuais)
            """

        """
            if (len(registroArestas) == posicaoRegistro) and ((posicaoListaCombinacoes + 1) != len(listaCombinacoes)):
                registroArestas.append(arestasAtuais)
                registroNodes.append(nodesAtuais)

        if (len(registroArestas) == posicaoRegistro) and (posicaoListaCombinacoes  != len(listaCombinacoes)):
            registroArestas.append(arestasAtuais)
            registroNodes.append(nodesAtuais)
        """

        posicaoRegistro -= 1
        arestasAtuais = registroArestas[posicaoRegistro]
        nodesAtuais = registroNodes[posicaoRegistro]

        listaElementosCyto = nodesAtuais + arestasAtuais

    elif input == "inputValorFiltro" and inputValorFiltro is not None:
        for aresta in arestasAtuais:
            aresta["classes"] = aresta["classes"].replace(" ocultar", "")

        # if (inputValorFiltro == default_media):
        #     #arestas = gerarArestas(dadosComparacaoJSONGlue)
        #     listaElementosCyto = nodesAtuais + arestasAtuais
        # else:
        if (inputValorFiltro != default_media):
            dadosFiltrados = []

            if (filtroAtivo == "DifMediaComp"):
                for aresta in arestasAtuais:
                    if (float(aresta["data"]["media_comprimento"]) > float(inputValorFiltro)):
                        aresta["classes"] += " ocultar"

                #dadosFiltrados = [conexao for conexao in dadosComparacaoJSONGlue if float(conexao[6]) <= float(inputValorFiltro)]
            elif (filtroAtivo == "DifDesvioPadrao"):
                for aresta in arestasAtuais:
                    if (float(aresta["data"]["desvio_padrao"]) > float(inputValorFiltro)):
                        aresta["classes"] += " ocultar"

                #dadosFiltrados = [conexao for conexao in dadosComparacaoJSONGlue if float(conexao[7]) <= float(inputValorFiltro)]

            # if(dadosFiltrados != []):
            #     arestas = gerarArestas(dadosFiltrados)
            #     listaElementosCyto = nodesAtuais + arestas
            listaElementosCyto = nodesAtuais + arestasAtuais

    elif input == "btConfirmarCorresp":
        for aresta in arestasAtuais:
            if(int(aresta["data"]["id"]) == int(arestaSelecionada["id"])):
                aresta["classes"] += " confirmado"
                break

        listaElementosCyto = nodesAtuais + arestasAtuais
        paresConfirmados.append(arestaSelecionada["id"])

    elif input == "btRecusarCorresp":
        for aresta in arestasAtuais:
            if(int(aresta["data"]["id"]) == int(arestaSelecionada["id"])):
                aresta["classes"] += " recusado"
                break

        listaElementosCyto = nodesAtuais + arestasAtuais
        paresRecusados.append(arestaSelecionada["id"])

    elif input == "dropdownFiltros":
        filtroAtivo = dropdownFiltros

    try:
        if (posicaoListaCombinacoes < len(listaCombinacoes)):
            nomesSchemas = obterNomesSchemas()
            titulo = "Esquema " + nomesSchemas[0] + ' vs Esquema ' + nomesSchemas[1] + ' - Porcentagem: ' + str((parte-1) * 20) + '% - ' + str(parte * 20) + '%\n'
        elif(len(listaCombinacoes) > 0):
            titulo = "Visão Geral dos Esquemas\n"
    except:
        None

    return listaElementosCyto, titulo

def runApp():
    app.run_server(debug=False)

if __name__ == "__main__":
    runApp()