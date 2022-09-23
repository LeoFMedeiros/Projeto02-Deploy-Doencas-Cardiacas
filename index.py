import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from app import *
import pickle
from lightgbm import LGBMClassifier


card_style = {
    'width': '800px',
    'min-height': '300px',
    'padding-top': '25px',
    'padding-right': '25px',
    'padding-left': '25px',
}

model = pickle.load(open("model.pkl", "rb"))


# =========  Layout  =========== #
app.layout = dbc.Container(children=[
        dbc.Card([
            dbc.Col([
                html.Legend("SISTEMA DE DETECÇÃO DE DOENÇAS CARDÍACAS", style={'text-align': 'center'}),
                dbc.Select(id="genero",options=[{"label": "HOMEM", "value": "1"},{"label": "MULHER", "value": "2"},{"label": "OUTRO", "value": "3"},],placeholder="GÊNERO", style={'margin-top': '5px'}),
                dbc.Input(id="idade", placeholder="INFORME A SUA IDADE", type="number", style={'margin-top': '5px'}),
                dbc.Input(id="altura", placeholder="INFORME A SUA ALTURA (CM)", type="number", style={'margin-top': '5px'}), 
                dbc.Input(id="peso", placeholder="INFORME A SEU PESO (KG)", type="number", style={'margin-top': '5px'}),
                dbc.Input(id="ap_hi", placeholder="INFORME A SUA PRESSÃO SISTÓLICA", type="number", style={'margin-top': '5px'}),
                dbc.Input(id="ap_lo", placeholder="INFORME A SUA PRESSÃO DIASTÓLICA", type="number", style={'margin-top': '5px'}),
                dbc.Select(id="colesterol",options=[{"label": "NORMAL", "value": "1"},{"label": "ACIMA DO NORMAL", "value": "2"},{"label": "BEM ACIMA DO NORMAL", "value": "3"},],placeholder="COLESTEROL", style={'margin-top': '5px'}),
                dbc.Select(id="glicose",options=[{"label": "NORMAL", "value": "1"},{"label": "ACIMA DO NORMAL", "value": "2"},{"label": "BEM ACIMA DO NORMAL", "value": "3"},],placeholder="GLICOSE", style={'margin-top': '5px'}),
                dbc.Select(id="fumante",options=[{"label": "SIM", "value": "1"},{"label": "NÃO", "value": "2"}],placeholder="FUMANTE", style={'margin-top': '5px'}),
                dbc.Select(id="alcool",options=[{"label": "SIM", "value": "0"},{"label": "NÃO", "value": "1"}],placeholder="USA BEBIDA ALCOÓLICA?", style={'margin-top': '5px'}),
                dbc.Select(id="active",options=[{"label": "SIM", "value": "0"},{"label": "NÃO", "value": "1"}],placeholder="FAZ ATIVIDADE FÍSICA", style={'margin-top': '5px'}),
                html.Span(id='span', style={"text-align": "center",'margin-top': '10px'}),               
                dbc.Button("RESULTADO", id="resultado", style={'margin-top': '5px'}),
            ], sm=12, md=12, lg=12,),    
        ], style=card_style, className="align-self-center")
], fluid=True, style={"height": "100vh", "display": "flex", "justify-content": "center"})

# ===================== CALLBACK =============================== #
@app.callback(
        Output('span', 'children'),
        Input('resultado', 'n_clicks'),
    [
        State('genero', 'value'),
        State('idade', 'value'),
        State('altura', 'value'),
        State('peso', 'value'),
        State('ap_hi', 'value'),
        State('ap_lo', 'value'),
        State('colesterol', 'value'),
        State('glicose', 'value'),
        State('fumante', 'value'),
        State('alcool', 'value'),
        State('active', 'value'),

    ]
)
def previsao(n, genero, idade, altura, peso, ap_li, ap_lo, colesterol, glicose, fumante, alcool, active):
    if n:
        print(genero, idade, altura, peso, ap_li, ap_lo, colesterol, glicose, fumante, alcool, active)
        if genero is None or idade is None or altura is None or peso  is None or ap_li is None or ap_lo is None or colesterol is None or glicose is None or fumante is None or alcool is None or active is None:
            return html.H5('PREENCHA TODOS OS VALORES', style={'color': 'red'}) 
        else:
            bmi = peso/((altura/100)**2)
            bpr = ap_li / ap_lo
            ap_sum = ap_li + ap_lo
            tabela = {
                'age '          : [idade],
                'height'        : [altura],
                'weight'        : [peso],
                'ap_hi'         : [ap_li],
                'ap_lo'         : [ap_lo],
                'bmi'           : [bmi],
                'bpr'           : [bpr],
                'ap_sum'       : [ap_sum],
                'gender_1'      : [0],
                'gender_2'      : [0],
                'gluc_1'       : [0],
                'gluc_2'        : [0],
                'gluc_3'        : [0],
                'cholesterol_1' : [0],
                'cholesterol_2' : [0],
                'cholesterol_3' : [0],
                'smoke_0'       : [0],
                'smoke_1'       : [0],
                'alco_0'        : [0],
                'alco_1'        : [0],
                'active_0'      : [0],
                'active_1'      : [0],
            }
            tabela = pd.DataFrame(tabela)

            if genero == 1:
                tabela.loc[0, 'gender_1'] = 1
            else:
                tabela.loc[0, 'gender_2'] = 1

            if glicose == 1:
                tabela.loc[0, 'gluc_1'] = 1
            elif glicose == 2:
                tabela.loc[0, 'gluc_2'] = 1
            else:
                tabela.loc[0, 'gluc_3'] = 1

            if colesterol == 1:
                tabela.loc[0, 'cholesterol_1'] = 1
            elif colesterol == 2:
                tabela.loc[0, 'cholesterol_2'] = 1
            else:
                tabela.loc[0, 'cholesterol_3'] = 1

            if fumante == 0:
                tabela.loc[0, 'smoke_0'] = 1
            else:
                tabela.loc[0, 'smoke_1'] = 1

            if active == 0:
                tabela.loc[0, 'active_0'] = 1
            else:
                tabela.loc[0, 'active_1'] = 1

            y_pred = model.predict(tabela)
            probabilidade = model.predict_proba(tabela)

            if y_pred == 0:
                probabilidade = probabilidade[0][0]
                probabilidade = (probabilidade * 100).round(2)
                resultado = f'NÃO TEM DOENÇA CARDÍACA COM UMA CONFIANÇA DE {probabilidade}%'
                resultado =  html.H5(resultado, style={'color': 'green', "text-align": "center",'margin-top': '10px'})
            if y_pred == 1:
                probabilidade = probabilidade[0][1]
                probabilidade = (probabilidade * 100).round(2)
                resultado = f'POSSÍVEL DOENÇA CARDÍCA COM UMA CONFIANÇA DE {probabilidade}%'
                resultado =  html.H5(resultado, style={'color': 'red', "text-align": "center",'margin-top': '10px'})

            return resultado


if __name__ == '__main__':
    app.run_server(debug=False)