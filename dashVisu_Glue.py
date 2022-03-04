import ast
import pandas as pd
import numpy as np
import random
import dash
import dash_cytoscape as cyto
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import os
import signal

import jsonglue_dash as jg

#SET OPTIONS DATAFRAME
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.float_format', lambda x: '%.0f' % x)

posicao_lista_comparacao = 0
parte = 1
lista_combinacoes = []

dicionario_num_node1 = {}
dicionario_num_node2 = {}
inv_dict_num_node = {}

json_node_listAll = []

dados = []
dados_reduzido = []

arestasAtuais = []

pares_confirmados = []
pares_recusados = []

arestaSelecionada = []

inputs = [["input_filtro_dif_comprimento","value"], ["btRecarregar","n_clicks"], ["btCarregarInicio","n_clicks"], ["btCarregarProximo","n_clicks"], ["btRecusarCorresp", "n_clicks"], ["btConfirmarCorresp", "n_clicks"]]


def obterNomesSchemas():
    tupla = lista_combinacoes[posicao_lista_comparacao]
    nomesSchemas = jg.obterNomesSchemas(tupla[0], tupla[1])
    return [str(nomesSchemas[0]),str(nomesSchemas[1])]


def carregaJsonGlue():
    global lista_combinacoes
    global inputSchemas
    jg.leituraSchemas("covidA.json covidB.json")
    #jg.leituraSchemas("caso1.json caso2.json caso3.json")
    #jg.leituraSchemas(inputSchemas)
    lista_combinacoes = jg.combinacoesSchemas


def compararSchema(parte):
    global dados
    global lista_combinacoes
    global posicao_lista_comparacao

    dados = []
    tupla = lista_combinacoes[posicao_lista_comparacao]
    comparacao = jg.compararSchemas(tupla[0], tupla[1], parte)

    lista_info_tratada = [elem for elem in comparacao[0][2] if len(elem) > 7]
    comparacao[0][2] = lista_info_tratada
    dados_brutos = comparacao[0][2]

    for dado in dados_brutos:
        if (dado[8][0] != None):
            dados.append(dado)

def carregaGrafo():
    global dados
    global dicionario_num_node1
    global dicionario_num_node2
    global inv_dict_num_node
    global json_node_listAll
    global arestasAtuais

    global inv_dicionario_num_node_all

    node_list1 = []
    node_list2 = []

    for i, row in enumerate(dados):
        v1 = row[0]
        v2 = row[3]
        node_list1.append(v1)
        node_list2.append(v2)


    node_list1 = list(dict.fromkeys(node_list1))
    node_list2 = list(dict.fromkeys(node_list2))
    node_listAll = list(dict.fromkeys(node_list1 + node_list2))


    dicionario_num_node1 = {}
    for i, node in enumerate(node_list1):
        dicionario_num_node1[node] = i

    dicionario_num_node2 = {}
    for i, node in enumerate(node_list2):
        dicionario_num_node2[node] = i + len(node_list1)

    #dict_num_node_all = {**dicionario_num_node1, **dicionario_num_node2}

    inv_dicionario_num_node1 = {dicionario_num_node1[k] : k for k in dicionario_num_node1}
    inv_dicionario_num_node2 = {dicionario_num_node2[k] : k for k in dicionario_num_node2}
    inv_dict_num_node = {**inv_dicionario_num_node1, **inv_dicionario_num_node2}

    json_node_list1 = gerar_nodes(node_list1,1,0)
    json_node_list2 = gerar_nodes(node_list2,2,len(dicionario_num_node1))
    json_node_listAll = json_node_list1 + json_node_list2

    arestasAtuais = gera_arestas(dados,len(inv_dict_num_node))

    elem_list = json_node_listAll + arestasAtuais

    return elem_list

def gerar_nodes(list,classes,first_id):
    return [
        {
            "data": {
                "id": str(first_id + i),
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
        for i, node in enumerate(list)
    ]

def gera_arestas(data, first_id):
    global dicionario_num_node1
    global dicionario_num_node2

    conn_list_out = list()

    for i, row in enumerate(data):
        v1 = row[0]
        v2 = row[3]

        temp_dict = {
            "data": {
                        "id": first_id + i,
                        "source": dicionario_num_node1[v1],
                        "target": dicionario_num_node2[v2],
                        "media_comprimento": row[6],
                        "desvio_padrao": row[7],
                        "histograma": row[8],
                     },
            "classes": "1",
            "locked": True,
        }

        conn_list_out.append(temp_dict)

    return conn_list_out


# ---------------------- GRAFO REDUZIDO ---------------------- #
def compararTodosSchemasReduzido():
    global dados_reduzido
    global lista_combinacoes

    for tupla in lista_combinacoes:
        comparacao = jg.compararSchemas(tupla[0], tupla[1], 0)
        lista_info_tratada = [elem for elem in comparacao[0][2] if len(elem) > 7]
        dados = lista_info_tratada

        qtd_dados = 0
        media_comprimento = 0
        desvio_padrao = 0

        hist0 = 0
        hist1 = 0
        hist2 = 0
        for comp in dados:
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

        dados_reduzido.append([comparacao[0][0], comparacao[0][1], str(media_media_comprimento), str(media_desvio_padrao), [str(media_hist0), str(media_hist1), str(media_hist2)]])

def carregaGrafoReduzido():
    global dados_reduzido
    global inv_dict_num_node

    node_list1 = []
    node_list2 = []

    for i, row in enumerate(dados_reduzido):
        v1 = row[0]
        v2 = row[1]
        node_list1.append(v1)
        node_list2.append(v2)

    node_list1 = list(dict.fromkeys(node_list1))
    node_list2 = list(dict.fromkeys(node_list2))
    node_listAll = list(dict.fromkeys(node_list1 + node_list2))

    dict_num_node_reduzido = {}
    for i, node in enumerate(node_listAll):
        dict_num_node_reduzido[node] = i

    inv_dict_num_node = {dict_num_node_reduzido[k] : k for k in dict_num_node_reduzido}

    json_node_listAll = gerar_nodes_reduzido(node_listAll,0)
    arestas = gera_arestas_reduzido(dados_reduzido,dict_num_node_reduzido)

    elem_list = json_node_listAll + arestas

    return elem_list

def gerar_nodes_reduzido(lista,first_id):
    return [
        {
            "data": {
                "id": str(first_id + i),
                "label": node,
                "title": node,
                "node_size": 10,
            },
            "position": {
                "x": i*65 + random.randint(100,300) #random.randint(1,100)*i
                ,"y": (first_id + i)*150 + random.randint(100,300)
            },
            "classes": str(first_id + i),
            "selectable": True,
            "grabbable": False,
        }
        for i, node in enumerate(lista)
    ]


def gera_arestas_reduzido(data, dict_num_node_reduzido):
    conn_list_out = list()
    for i, row in enumerate(data):
        v1 = row[0]
        v2 = row[1]

        temp_dict = {
            "data": {
                "source": dict_num_node_reduzido[v1],
                "target": dict_num_node_reduzido[v2],
                "media_comprimento": row[2],
                "desvio_padrao": row[3],
                "histograma": row[4],
            },
            "classes": "1",
            "locked": True,
        }

        conn_list_out.append(temp_dict)

    return conn_list_out

"""
def carregaDados(grafoJsonGlue):
    global dados
    #f = open("saida.txt","r")
    #var = f.read()
    #f.close()
    #var = ast.literal_eval(grafoJsonGlue)

    dados = grafoJsonGlue[0][2]
    #print(dados)
"""

startup_elem_list = []
actual_elem_list = startup_elem_list

default_media = 1
titulo = ""

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
body_layout = html.Div(
    [
        html.Br(),
        dbc.Row(
            [
                #dbc.Badge(
                #    "Digite os schemas para análise:", color="info", className="mr-1", style={"height": "50%"}
                #),

                dbc.FormGroup(
                    [
                        dcc.Input(
                            id="input_schemas",
                            placeholder = 'Digite os schemas',
                            type = 'text',
                            value = ""
                        )
                    ]
                ),
                html.Hr(),
                dbc.Button("Carregar 1º Matching", color="primary", className="mr-1", id="btCarregarInicio", n_clicks=0, size="sm", style={"height": "50%"}),
                html.Hr(),
                dbc.Button("Carregar Próximo Matching", color="primary", className="mr-1", id="btCarregarProximo", n_clicks=0, size="sm", style={"height": "50%"}),
                html.Hr(),
                dbc.Button("Recarregar Matching Atual", color="primary", className="mr-1", id="btRecarregar", n_clicks=0, size="sm", style={"height": "50%"}),
                html.Hr(),
            ]
        ),
        dbc.Row(
            [
                html.Br(),

                dbc.Badge(
                    "Filtros", color="light", className="mr-1", style={"height": "50%", "font-size": "medium"}
                ),

                dbc.Badge(
                    "Diferença nas médias de comprimento:", color="info", className="mr-1", style={"height": "50%"}
                ),
                dbc.FormGroup(
                    [
                        dcc.Input(
                            id="input_filtro_dif_comprimento",
                            placeholder = 'Digite um valor...',
                            type = 'number',
                            value = default_media
                        )
                    ]
                ),

                html.Div(id='output_schemas', style='visibility: hidden')
            ]
        ),
        dbc.Row(
                html.H5(titulo, id="titulo_H5", style={'textAlign': 'center'})
        ),
        dbc.Row(
            [
                cyto.Cytoscape(
                    id="core_19_cytoscape",
                    layout={"name": "preset"},
                    style={"width": "100%", "height": "500px"},
                    elements=startup_elem_list,
                    #stylesheet=def_stylesheet,
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
                        }
                    ]
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Alert(
                        id="node-data",
                        children="Detalhes do elemento do esquema",
                        color="secondary",
                    )
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            dbc.Alert(
                                id="edge-data",
                                children="Detalhes da correspondência dos elementos",
                                color="secondary",
                            )
                        ),
                        dbc.Row(
                            [
                                dbc.Button("Confirmar Correspondência", color="success", className="mr-1", id="btConfirmarCorresp", n_clicks=0,
                                               size="sm", style={"height": "50%"}),
                                dbc.Button("Recusar Correspondência", color="danger", className="mr-1", id="btRecusarCorresp", n_clicks=0,
                                           size="sm", style={"height": "50%"})
                            ]
                        )
                    ]
                )
            ]
        ),
        html.Br()

    ], style={"margin-left": "5%", "margin-right": "5%"}
)

app.layout = html.Div([body_layout])

inputSchemas = ""

@app.callback(
    Output("output_schemas", "children"), Input("input_schemas", "value")
)
def salvarInputSchemas(value):
    global inputSchemas
    inputSchemas = value
    #print(inputSchemas)
    return value

@app.callback(
    Output("edge-data", "children"), Input("core_19_cytoscape", "selectedEdgeData")
)
def display_edgedata(edge):
    global arestaSelecionada

    contents = []
    contents.append(html.H6("Detalhes da correspondência selecionada"))

    if edge is not None:
        if(len(edge) > 0):
            data = edge[0]
            arestaSelecionada = data
            #data['target'].connectedEdges().style({'line-color': 'red'})

            nomesSchemas = obterNomesSchemas()

            contents.append(html.Br())
            #contents.append(html.H5("Title: " + data["id"].title()))
            contents.append(
                html.H6(
                    "Elemento do esquema " + nomesSchemas[0] + ": " + inv_dict_num_node[int(data["source"])]
                )
            )
            contents.append(
                html.H6(
                     "Elemento do esquema " + nomesSchemas[1] + ": " + inv_dict_num_node[int(data["target"])]
                )
            )
            contents.append(
                html.P(
                    "Diferença na média dos comprimentos dos dados (AVG): " + str(data['media_comprimento'])
                )
            )
            contents.append(
                html.P(
                    "Diferença no desvio padrão dos dados (STD): " + str(data['desvio_padrao'])
                )
            )
            contents.append(
                html.P(
                    "Análise histograma: " + ",".join(data['histograma'])
                )
            )
            """
            contents.append(
                dbc.Row(
                    [
                        dbc.Button("Confirmar Correspondência", color="success", className="mr-1", id="btConfirmarCorresp", n_clicks=0,
                                   size="sm", style={"height": "50%"}),
                        dbc.Button("Recusar Correspondência", color="danger", className="mr-1", id="btRecusarCorresp", n_clicks=0,
                                   size="sm", style={"height": "50%"})
                    ]
                )
            )
            """

    return contents

@app.callback(
    Output("node-data", "children"), [Input("core_19_cytoscape", "selectedNodeData")]
)
def display_nodedata(datalist):
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

@app.callback(
    [
        Output("core_19_cytoscape", "elements"),
        Output("titulo_H5", "children")
    ],
    [

        Input('{}'.format(input[0]), '{}'.format(input[1])) for input in inputs
    ],
)
def acoesBotoes(input_media, btRecarregar, btCarregarInicio, btCarregarProximo, btConfirmarCorresp, btRecusarCorresp):
    global actual_elem_list
    global posicao_lista_comparacao
    global parte

    ctx = dash.callback_context
    input = ctx.triggered[0]['prop_id'].split('.')[0]

    titulo = ""

    if input == "btRecarregar":
        if (posicao_lista_comparacao < len(lista_combinacoes)):
            actual_elem_list = carregaGrafo()
        elif(len(lista_combinacoes) > 0):
            actual_elem_list = carregaGrafoReduzido()

    elif input == "btCarregarInicio":
        carregaJsonGlue()
        posicao_lista_comparacao = 0

        compararSchema(1)
        actual_elem_list = carregaGrafo()
        #compararTodosSchemasReduzido()
        #actual_elem_list = carregaGrafoReduzido()

    elif input == "btCarregarProximo": # COLOCAR TRAVA!

        parte = parte + 1

        if (parte > 5):
            parte = 1
            posicao_lista_comparacao = posicao_lista_comparacao + 1

        if (posicao_lista_comparacao < len(lista_combinacoes)):
            compararSchema(parte)
            actual_elem_list = carregaGrafo()

        elif (posicao_lista_comparacao == len(lista_combinacoes)):
            compararTodosSchemasReduzido()
            actual_elem_list = carregaGrafoReduzido()
            posicao_lista_comparacao = posicao_lista_comparacao + 1

    elif input == "input_filtro_dif_comprimento" and input_media is not None:
        if (input_media == default_media):
            arestas = gera_arestas(dados)
            actual_elem_list = json_node_listAll + arestas
        else:
            dados_filtrados = [conexao for conexao in dados if float(conexao[6]) <= float(input_media)]
            arestas = gera_arestas(dados_filtrados)
            actual_elem_list = json_node_listAll + arestas

    elif input == "btConfirmarCorresp":
        for aresta in arestasAtuais:
            if(int(aresta["data"]["id"]) == int(arestaSelecionada["id"])):
                aresta["classes"] += " confirmado"

        actual_elem_list = json_node_listAll + arestasAtuais
        pares_confirmados.append(arestaSelecionada["id"])

    elif input == "btRecusarCorresp":
        for aresta in arestasAtuais:
            if(int(aresta["data"]["id"]) == int(arestaSelecionada["id"])):
                aresta["classes"] += " recusado"

        actual_elem_list = json_node_listAll + arestasAtuais
        pares_recusados.append(arestaSelecionada["id"])


    try:
        if (posicao_lista_comparacao < len(lista_combinacoes)):
            nomesSchemas = obterNomesSchemas()
            titulo = "Esquema " + nomesSchemas[0] + ' vs Esquema ' + nomesSchemas[1] + ' - Porcentagem: ' + str(parte * 20) + '%\n'
        elif(len(lista_combinacoes) > 0):
            titulo = "Visão Geral dos Schemas\n"
    except:
        None


    return actual_elem_list, titulo

def runApp():
    app.run_server(debug=False)

if __name__ == "__main__":
    runApp()