import json
import urllib
from ast import literal_eval


import dash_html_components as html
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import pickle
from app import app
from dash.dependencies import Input, Output
import plotly.graph_objects as go

url = 'https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json'
response = urllib.request.urlopen(url)
data = json.loads(response.read())


layout = html.Div([
    dbc.Row([
        dbc.Col([html.P("Chart Type:")], width=1),
        dbc.Col([dcc.Dropdown(id='chart-dd',
                   options=[{'label': 'Q2 Portfolio', 'value': 'portfolio'},
                            {'label': 'Q3 Portfolio', 'value': 'ordered'}],
                   value='portfolio',
                   className='dash-bootstrap')], width=2),
    ]),
    dcc.Graph(id="graph"),


])
def get_spreadsheet_data(filename):
    df = pd.read_excel(filename)
    node = dict(zip(df['Key'], df['node']))
    link = dict(zip(df['Key'], df['link']))
    ret_node = {}
    ret_link = {}
    for k, v in node.items():
        if k in ['line', 'label', 'color']:
            ret_node[k] = literal_eval(v)

    for k, v in link.items():
        # if k in ['label', 'color', 'source', 'target', 'value']:
        if k in ['color', 'source', 'target', 'value']:
            ret_link[k] = literal_eval(v)
    return ret_node, ret_link



@app.callback(
    Output("graph", "figure"),
    [Input("chart-dd", "value")])
def display_sankey(chart_type):
    if chart_type == 'ordered':
        node, link = get_spreadsheet_data('assets/Sankey Portfolio Ordered.xlsx')
        fig = go.Figure(go.Sankey(link=link, node=node))
        fig.update_layout(font=dict(size=18, color='white'), height=1050, plot_bgcolor='#222', paper_bgcolor='#222',
                          title="Change in Portfolio Composition Q2->Q3"
                          )
    else:
        node, link = get_spreadsheet_data('assets/Sankey Portfolio.xlsx')
        fig = go.Figure(go.Sankey(link=link, node=node))
        fig.update_layout(font=dict(size=18, color='white'), height=1050, plot_bgcolor='#222', paper_bgcolor='#222', )

        fig.update_layout(
            hovermode='x',
            title="Change in Portfolio Composition Q1->Q2",
            font=dict(size=18, color='white'),
            height=1050,
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            # color_discrete_map=cmap,
        )

    return fig

