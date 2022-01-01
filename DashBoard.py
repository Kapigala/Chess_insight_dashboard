# Niezbędne biblioteki
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np
import json
import os

# Translacja nazw federacji na ISO3
deco = {'URU': 'URY', 'SUI': 'CHE', 'CHI': 'CHL', 'ENG': 'GBR', 'NED': 'NLD', 'POR': 'PRT', 'GER': 'DEU',
        'LAT': 'LVA', 'PAR': 'PRY', 'MGL': 'MNG', 'CRO': 'HVO', 'KSA': 'SAU', 'IRI': 'IRN', 'GRE': 'GRC'}
# lista wartości dla suwaków/kolumn
lata = ['All', '1921-1934', '1935-1945', '1946-1956', '1957-1967', '1968-1978', '1979-1989', '1990-2000', '2001-2011']
h = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'fide_id']

with open('custom.geo.json') as response:
    countries = json.load(response)

# Wczytanie zbioru graczy
file_path = 'players.csv'
gracze = pd.read_csv(file_path)
# Redukcja o zawodników amatorskich
gracze = gracze[gracze['title'].isnull() == False]

# Inicjacja aplikacji
app = dash.Dash()


# --Definicje--
def df_init(rok, miesiac, tempo):
    global gracze
    dane = pd.read_csv('./data/chess_{}_rating_{}.csv'.format(rok, tempo), names=h)
    df = pd.merge(gracze, dane, on='fide_id')
    df = df[df['title'].isin(['WCM', 'CM', 'WFM', 'FM', 'WIM', 'IM', 'WGM', 'GM']) == True]
    df = df[df[miesiac].isnull() == False]
    return df


def box(rok='2020', miesiac='Dec', tempo='standard'):
    dd = df_init(rok, miesiac, tempo)
    dd.loc[dd['gender'] == 'F', 'gender'] = 'Kobiety'
    dd.loc[dd['gender'] == 'M', 'gender'] = 'Mężczyźni'
    fig = px.box(dd, x='gender', y=miesiac, title="Porównanie ELO w zależności od płci", labels={
        "gender": 'Płeć',
        miesiac: "ELO Rating"}, color='gender', height=600)
    return fig


def linepll(tempo='standard'):
    df = pd.read_csv('szereg.csv', names=['tempo', 'data', 'fide_id', 'Elo'])
    df = df[df['tempo'] == tempo]
    fig = px.line(df, x='data', y='Elo', color='fide_id', title='ELO dla szachów {}'.format(tempo))
    return fig


def hist_b(lata='1990-2000'):
    global gracze
    if lata == 'All':
        fig = px.histogram(gracze['federation'],
                           height=800,
                           title='Liczba utytułowanych zawodników').update_xaxes(categoryorder='total descending')
        return fig
    else:
        fig = px.histogram(gracze[(gracze['yob'] < int(lata[5:9])) & (gracze['yob'] > int(lata[0:4]))]['federation'],
                           height=800,
                           title='Liczba utytułowanych zawodników urodzonych w latach {}'.format(lata)).update_xaxes(
            categoryorder='total descending')
        return fig


def pie_chart(lata='1979-1989'):
    if lata != 'All':
        df_1 = gracze[(gracze['yob'] < int(lata[5:9])) & (gracze['yob'] > int(lata[0:4]))]
        tyt = 'Utytułowani zawodnicy urodzeni w latach {}'.format(lata)
    else:
        df_1 = gracze
        tyt = 'Wszyscy utytułowani zawodnicy'

    df = pd.DataFrame(columns=['federation', 'count'])
    for i in df_1['federation'].unique():
        df = df.append({'federation': i, 'count': df_1['federation'].value_counts()[i]}, ignore_index=True)
    df = df[df['count'] > 0.01 * df['count'].sum()]

    fig = px.pie(df, values='count', names='federation', title=tyt)
    return fig


def bar_chart(lista=['POL', 'RUS', 'GER', 'ESP', 'IND']):
    df_1 = gracze[gracze['federation'].isin(lista) == True]
    df = pd.DataFrame(columns=['federation', 'title', 'count'])
    for i in df_1['federation'].unique():
        for title_1 in ['WCM', 'CM', 'WFM', 'FM', 'WIM', 'IM', 'WGM', 'GM']:
            df = df.append({'federation': i, 'title': title_1,
                            'count': df_1[(df_1['federation'] == i) & (df_1['title'] == title_1)].shape[0]},
                           ignore_index=True)
    fig = px.bar(df, x="federation", y='count',
                 color="title",
                 title="Tytuły w federacji")
    return fig


def hist_a(rok='2020', miesiac='Dec', tempo='standard'):
    global gracze
    dane = pd.read_csv('./data/chess_{}_rating_{}.csv'.format(rok, tempo), names=h)
    dane = dane.dropna()
    dane['data'] = '{}-{}'.format(rok, h.index(miesiac) + 1)
    fig = px.histogram(dane[miesiac],
                       height=800,
                       title='Rozkład Elo',
                       marginal='violin')
    return fig


def mapa(tryb='AVG_ELO', rok='2020', miesiac='Dec', tempo='standard'):
    c = []
    df_base = df_init(rok, miesiac, tempo)
    for i in deco.keys():
        df_base.loc[df_base['federation'] == i, 'federation'] = deco[i]

    df = pd.DataFrame(columns=['federation', 'title', 'count'])
    for i in df_base['federation'].unique():
        for title_1 in ['WCM', 'CM', 'WFM', 'FM', 'WIM', 'IM', 'WGM', 'GM']:
            df = df.append({'federation': i, 'title': title_1,
                            'count': df_base[(df_base['federation'] == i) & (df_base['title'] == title_1)].shape[0]},
                           ignore_index=True)

    if tryb == 'AVG_ELO' or tryb == 'MAX_ELO':
        if tryb == 'AVG_ELO':
            rankingi = df_base.groupby("federation").mean().round()[miesiac]
            c = pd.DataFrame({'federation': rankingi.index.array, 'AVG_elo': rankingi.array})
        elif tryb == 'MAX_ELO':
            rankingi = df_base.groupby("federation").max()[miesiac]
            c = pd.DataFrame({'federation': rankingi.index.array, 'MAX_elo': rankingi.array})

        fig = px.choropleth(c,
                            geojson=countries,
                            locations='federation',
                            locationmode='ISO-3',
                            color='{}_elo'.format(tryb[0:3]),
                            color_continuous_scale="Viridis",
                            labels={'{}_elo'.format(tryb[0:3]): '{} Ranking utytułowanego zawodnika w kraju'.format(
                                tryb[0:3])}
                            )
        return fig
    else:
        if tryb == 'GM_COUNT':
            c = df[df['title'] == 'GM'].sort_values(by=['count'], ascending=False)
        elif tryb == 'IM_COUNT':
            c = df[df['title'] == 'IM'].sort_values(by=['count'], ascending=False)
        elif tryb == 'WGM_COUNT':
            c = df[df['title'] == 'WGM'].sort_values(by=['count'], ascending=False)
        elif tryb == 'WIM_COUNT':
            c = df[df['title'] == 'WIM'].sort_values(by=['count'], ascending=False)
        elif tryb == 'FM_COUNT':
            c = df[df['title'] == 'FM'].sort_values(by=['count'], ascending=False)
        elif tryb == 'WFM_COUNT':
            c = df[df['title'] == 'WFM'].sort_values(by=['count'], ascending=False)
        elif tryb == 'WCM_COUNT':
            c = df[df['title'] == 'WCM'].sort_values(by=['count'], ascending=False)
        elif tryb == 'CM_COUNT':
            c = df[df['title'] == 'CM'].sort_values(by=['count'], ascending=False)

        fig = px.choropleth(c,
                            geojson=countries,
                            locations='federation',
                            locationmode='ISO-3',
                            color='count',
                            color_continuous_scale="Viridis",
                            range_color=(int(c['count'].min()), int(c['count'].max())),
                            labels={'count': 'Liczba {}'.format(tryb[0:2])}
                            )
        return fig


##Generowanie wykresów
box_fig = box()
line_fig = linepll()
hist_fig = hist_b()
pie_fig = pie_chart()
bar_fig = bar_chart()
hist_elo_fig = hist_a()
map_fig = mapa()

# Ustawienia layout
app.layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(id='suwak_1',
                     options=[{'label': i, 'value': i} for i in ['2015', '2016', '2017', '2018', '2019', '2020']],
                     value='2020', placeholder='Select year'),
        dcc.Dropdown(id='suwak_2', options=[{'label': i, 'value': i} for i in ['standard', 'rapid', 'blitz']],
                     value='standard'),
        dcc.Dropdown(id='suwak_3', options=[{'label': i, 'value': i} for i in
                                            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct',
                                             'Nov', 'Dec']], value='Dec', placeholder='Select month'),
        dcc.Dropdown(id='suwak_4', options=[{'label': i, 'value': i} for i in np.sort(gracze['federation'].unique())],
                     value=['POL', 'RUS', 'GER', 'ESP', 'IND'], placeholder='Select country', multi=True),
        dcc.Dropdown(id='suwak_5',
                     options=[{'label': i, 'value': i} for i in ['GM', 'WGM', 'CM', 'WCM', 'IM', 'WIM', 'FM', 'WFM']],
                     value='GM', placeholder='Select title'),
        dcc.Dropdown(id='suwak_6', options=[{'label': i, 'value': i} for i in
                                            ['AVG_ELO', 'MAX_ELO', 'GM_COUNT', 'IM_COUNT', 'WGM_COUNT', 'WIM_COUNT']],
                     value='AVG_ELO', placeholder='Select feature'),
        dcc.Dropdown(id='suwak_7', options=[{'label': i, 'value': i} for i in lata], value='1990-2000',
                     placeholder='Select years')
    ]),
    html.Div([
        html.H1(children='1. Siła_gry'),
        html.Div(children='Modyfikacje: [rok,miesiąc,tempo]'),
        dcc.Graph(id='graph', figure=box_fig)
    ]),
    html.Div([
        html.H1(children='2. Postęp wybranych zawodników'),
        html.Div(children='Modyfikacje: [tempo]'),
        dcc.Graph(
            id='graph2',
            figure=line_fig
        ),
    ]),
    html.Div([
        html.H1(children='3.1 Liczba tytułów szachowych według kraju'),
        html.Div(children='Modyfikacje: [lata]'),
        dcc.Graph(
            id='graph3',
            figure=hist_fig
        ),
    ]),
    html.Div([
        html.H1(children='3.2 Federacje na przestrzeni dekad'),
        html.Div(children='Modyfikacje: [lata]'),
        dcc.Graph(id='graph4', figure=pie_fig)
    ]),
    html.Div([
        html.H1(children='3.3 Podział tytułów w krajach'),
        html.Div(children='Modyfikacje: [kraje]'),
        dcc.Graph(
            id='graph5',
            figure=bar_fig
        ),
    ]),
    html.Div([
        html.H1(children='4 Rozkład rankingowy'),
        html.Div(children='Modyfikacje: [tempo,rok,miesiąc]'),
        dcc.Graph(
            id='graph6',
            figure=hist_elo_fig
        ),
    ]),
    html.Div([
        html.H1(children='5. Szachowa mapa świata'),
        html.Div(children='Modyfikacje: [tempo,rok,miesiąc,tryb]'),
        dcc.Graph(
            id='graph7',
            figure=map_fig
        ),
    ]),
])


# Callbacks
@app.callback(
    Output(component_id='graph', component_property='figure'),
    [Input(component_id='suwak_1', component_property='value'),
     Input(component_id='suwak_2', component_property='value'),
     Input(component_id='suwak_3', component_property='value')
     ]
)
def update_graph(new_val, new_value_2, new_value_3):
    box_fig = box(rok=new_val, miesiac=new_value_3, tempo=new_value_2)
    return box_fig


@app.callback(
    Output(component_id='graph2', component_property='figure'),
    [Input(component_id='suwak_2', component_property='value')
     ]
)
def update_graph2(v1):
    line_fig = linepll(v1)
    return line_fig


@app.callback(
    Output(component_id='graph3', component_property='figure'),
    [Input(component_id='suwak_7', component_property='value')
     ]
)
def update_graph3(v1):
    hist_fig = hist_b(v1)
    return hist_fig


@app.callback(
    Output(component_id='graph4', component_property='figure'),
    [Input(component_id='suwak_7', component_property='value')
     ]
)
def update_graph4(v2):
    pie_fig = pie_chart(v2)
    return pie_fig


@app.callback(
    Output(component_id='graph5', component_property='figure'),
    [Input(component_id='suwak_4', component_property='value')],

)
def update_graph5(v2):
    bar_fig = bar_chart(v2)
    return bar_fig


@app.callback(
    Output(component_id='graph6', component_property='figure'),
    [Input(component_id='suwak_1', component_property='value'),
     Input(component_id='suwak_2', component_property='value'),
     Input(component_id='suwak_3', component_property='value')
     ]
)
def update_graph6(v1, v2, v3):
    hist_elo_fig = hist_a(v1, v3, v2)
    return hist_elo_fig


@app.callback(
    Output(component_id='graph7', component_property='figure'),
    [Input(component_id='suwak_6', component_property='value'),
     Input(component_id='suwak_1', component_property='value'),
     Input(component_id='suwak_3', component_property='value'),
     Input(component_id='suwak_2', component_property='value')
     ]
)
def update_graph7(v1, v2, v3, v4):
    map_fig = mapa(v1, v2, v3, v4)
    return map_fig


# Uruchamianie lokalne
# if __name__ == '__main__':
#   app.run_server(debug=True)

app.run_server(debug=True, port=os.getenv('PORT', '8050'), host="0.0.0.0")
