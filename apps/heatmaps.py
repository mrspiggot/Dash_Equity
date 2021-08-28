from app import app
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import yahoo_fin.stock_info as si
from datetime import date
import plotly.graph_objects as go
from datetime import date, timedelta
import plotly.express as px
import pandas as pd

term_dictionary = {1: '1 Month',2: '2 Months', 3: '3 Months', 4: '6 Months', 5: '1 Year', 6: '2 Years'}

layout = html.Div([
    html.H3('Performance Heatmap: Area is position size, Colour is Position Gain/Loss', style={'textAlign': 'center'}),
    dbc.Row([
        dbc.Col(
            dcc.Slider(min=1, max=6, marks=term_dictionary, id="sector-treemap-slider", value=1),
            width=4, lg={'size': 4,  "offset": 1, 'order': 'first'}
        ),
        dbc.Col(html.H5('Move Slider to see gains (losses) over different timeframes'),
            width=4, lg={'size': 4,  "offset": 0}),
        dbc.Col(
            dcc.Slider(min=1, max=2, marks={1: "Yes", 2: "No"}, id="sector-include-slider", value=2),
            width=1, lg={'size': 1,  "offset": 0}),
        dbc.Col(html.H5('Include Stock Type?'),
            width=2, lg={'size': 1, "offset": 0, 'order': 'last'}),
    ]),
    dbc.Spinner(dcc.Graph(id='sector-treemap', figure = {},), color='primary',),
])
@app.callback(Output('sector-treemap', 'figure'),
              [Input('sector-treemap-slider', 'value'),
               Input('sector-include-slider', 'value')])
def treemap(value, include_type):
    port = pd.read_excel('assets/Historical Performance.xlsx')

    port["portfolio"] = "Portfolio"
    port["Value"] = port['Yesterday Close'] - port[term_dictionary[value]]
    port["Gain"] = port["Value"] / port['Yesterday Close']
    port = port.round(2)

    if include_type == 1:
        tree_path = ['portfolio', 'Type', 'Industry', 'Sector', 'Ticker']
    else:
        tree_path = ['portfolio', 'Industry', 'Sector', 'Ticker']


    fig = px.treemap(port, path=tree_path, values='Yesterday Close', color='Gain',
                     color_continuous_scale='thermal', height=780,)
    fig.data[0].textinfo = 'label+value+percent parent'
    fig.layout.plot_bgcolor='#222'
    fig.layout.paper_bgcolor='#222'
    fig.update_layout(font_color='#29E')
    return fig