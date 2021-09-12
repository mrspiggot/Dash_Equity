from app import app
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import pickle


slider_dict = {0: '1 Month', 1: "2 Months", 2: '3 Months', 3: '6 Months', 4: '1 Year', 5: '2 Years'}
with open('assets/dropdown.pickle', 'rb') as handle:
    benchmark_dict = pickle.load(handle)

with open('assets/ticker.pickle', 'rb') as handle:
    ticker_dict = pickle.load(handle)

CHART_HEIGHT = 500

layout = html.Div([
        dbc.Row([
            dbc.Col(
                dcc.Slider(min=0, max=5, marks=slider_dict, id="term-slider", value=3),

            width={"size": 3, "offset": 4}),
            dbc.Col(html.H6('Benchmark term'),

            ),


        ]),
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='index-dd',
                    options=benchmark_dict['Stock Index'],
                    value=['^FTMC', '^IXIC', '^GSPC'],
                    multi=True,
                    className='dash-bootstrap'
                ),
            width=6),
            dbc.Col(
                dcc.Dropdown(
                    id='pm-dd',
                    options=benchmark_dict['Precious Metals'],
                    value=['SLV', 'GLD', 'PPLT'],
                    multi=True,
                    className='dash-bootstrap'
                ),
                width=6),
        ]),
        dbc.Row([

        dbc.Col(
            dcc.Loading(
                dcc.Graph(id='stock_index_chart'),
                type='graph',
                fullscreen=False),

            width=6),
        dbc.Col(
            dcc.Loading(
                dcc.Graph(id='metals_chart'),
                type='graph',
                fullscreen=False),

            width=6),
        ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='en-dd',
                options=benchmark_dict['Energy Future'],
                value=['QG=F', 'BZ=F', 'MTF=F'],
                multi=True,
                className='dash-bootstrap'
            ),
            width=6),
        dbc.Col(
            dcc.Dropdown(
                id='ag-dd',
                options=benchmark_dict['Agriculture'],
                value=['JO', 'CORN', 'CATL.L'],
                multi=True,
                className='dash-bootstrap'
            ),
            width=6),
    ]),
    dbc.Row([

        dbc.Col(
            dcc.Loading(
                dcc.Graph(id='energy_chart'),
                type='graph',
                fullscreen=False),

            width=6),
        dbc.Col(
            dcc.Loading(
                dcc.Graph(id='ag_chart'),
                type='graph',
                fullscreen=False),

            width=6),
    ]),

])
@app.callback(Output('stock_index_chart', 'figure'),
              [Input('term-slider', 'value'),
               Input('index-dd', 'value')])
def equity_index_chart(svalue, ivalue):

    df = pd.read_excel('assets/' + slider_dict[svalue] + '.xlsx')
    df.dropna(inplace=True)
    df['Date'] = pd.to_datetime(df['Unnamed: 0'], format='%d/%m/%Y')
    df.set_index('Unnamed: 0', inplace=True)

    data_list = []
    data = go.Scatter(
        x=df.Date,
        y=df['Portfolio'],
        name='Portfolio',
        mode='lines',
        connectgaps=True,

    )
    data_list.append(data)
    for ticker in ivalue:
        # print(ticker, index_dict[ticker])
        data = go.Scatter(
            x=df.Date,
            y = df[ticker],
            name=ticker_dict[ticker],
            mode='lines',
            opacity=0.45,
            connectgaps=True,
        )
        data_list.append(data)




    return {'data': data_list,
            'layout': go.Layout(title='Equity Benchmarks', xaxis=dict(range=[min(df.index), max(df.index)], title='Date', ),
                                plot_bgcolor='#222',
                                paper_bgcolor='#222',
                                font=dict(color='#58C'),
                                height=CHART_HEIGHT,
                                )

            }


@app.callback(Output('metals_chart', 'figure'),
              [Input('term-slider', 'value'),
               Input('pm-dd', 'value')])
def metals_index_chart(svalue, ivalue):

    df = pd.read_excel('assets/' + slider_dict[svalue] + '.xlsx')

    df.dropna(inplace=True)
    df['Date'] = pd.to_datetime(df['Unnamed: 0'], format='%d/%m/%Y')
    df.set_index('Unnamed: 0', inplace=True)

    data_list = []
    data = go.Scatter(
        x=df.Date,
        y=df['Portfolio'],
        name='Portfolio',
        mode='lines',
        connectgaps=True

    )
    data_list.append(data)
    for ticker in ivalue:
        # print(ticker, index_dict[ticker])
        data = go.Scatter(
            x = df.Date,
            y = df[ticker],
            name=ticker_dict[ticker],
            mode='lines',
            opacity=0.45,
            connectgaps=True,
        )
        data_list.append(data)




    return {'data': data_list,
            'layout': go.Layout(title='Precious Metals Benchmarks', xaxis=dict(range=[min(df.index), max(df.index)], title='Date'),
                                plot_bgcolor='#222',
                                paper_bgcolor='#222',
                                font=dict(color='#58C'),
                                height=CHART_HEIGHT,
                                )

            }


@app.callback(Output('energy_chart', 'figure'),
              [Input('term-slider', 'value'),
               Input('en-dd', 'value')])
def energy_index_chart(svalue, ivalue):

    df = pd.read_excel('assets/' + slider_dict[svalue] + '.xlsx')


    df.dropna(inplace=True)
    df['Date'] = pd.to_datetime(df['Unnamed: 0'], format='%d/%m/%Y')
    df.set_index('Unnamed: 0', inplace=True)
    data_list = []
    data = go.Scatter(
        x=df.Date,
        y=df['Portfolio'],
        name='Portfolio',
        mode='lines',
        connectgaps=True

    )
    data_list.append(data)
    for ticker in ivalue:
        # print(ticker, index_dict[ticker])
        data = go.Scatter(
            x = df.Date,
            y = df[ticker],
            name=ticker_dict[ticker],
            mode='lines',
            opacity=0.45,
            connectgaps=True,
        )
        data_list.append(data)




    return {'data': data_list,
            'layout': go.Layout(title='Energy Benchmarks', xaxis=dict(range=[min(df.index), max(df.index)], title='Date'),
                                plot_bgcolor='#222',
                                paper_bgcolor='#222',
                                font=dict(color='#58C'),
                                height=CHART_HEIGHT,
                                )

            }


@app.callback(Output('ag_chart', 'figure'),
              [Input('term-slider', 'value'),
               Input('ag-dd', 'value')])
def agriculture_index_chart(svalue, ivalue):

    df = pd.read_excel('assets/' + slider_dict[svalue] + '.xlsx')

    df.dropna(inplace=True)
    df['Date'] = pd.to_datetime(df['Unnamed: 0'], format='%d/%m/%Y')
    df.set_index('Unnamed: 0', inplace=True)
    data_list = []
    data = go.Scatter(
        x=df.Date,
        y=df['Portfolio'],
        name='Portfolio',
        mode='lines',
        connectgaps=True

    )
    data_list.append(data)
    for ticker in ivalue:
        # print(ticker, index_dict[ticker])
        data = go.Scatter(
            x = df.Date,
            y = df[ticker],
            name=ticker_dict[ticker],
            mode='lines',
            opacity=0.45,
            connectgaps=True,
        )
        data_list.append(data)




    return {'data': data_list,
            'layout': go.Layout(title='Agriculturals Benchmarks', xaxis=dict(range=[min(df.index), max(df.index)], title='Date'),
                                plot_bgcolor='#222',
                                paper_bgcolor='#222',
                                font=dict(color='#58C'),
                                height=CHART_HEIGHT,
                                )

            }
