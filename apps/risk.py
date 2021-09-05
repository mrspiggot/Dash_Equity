from app import app
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from utils.generate_portfolio_data import Risk
from scipy.stats import norm
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

conf_dict = {"display": {0: '95', 1: '99', 2: '99.5'},
             "calculate" : {0: 0.05, 1: 0.01, 2: 0.005}}
term_dict = {"display": {0: "1_day", 1: "1_week", 2: "1_Month"},
             "calculate": {0: 1, 1: 5, 2: 21}}
risk = Risk('assets/Sample Portfolio.xlsx')

def df_to_plotly(df):
    return {'z': (df.values*10000).tolist(),
            'x': df.columns.tolist(),
            'y': df.index.tolist()}

def correlation_surface():
    cov = pd.DataFrame(risk.cov)

    fig = go.Figure(data=[go.Surface(x=cov.columns.tolist(), y=cov.index.tolist(), z=cov.values*10000)])
    fig.update_layout(autosize=False, width=1470, height=1020, title="Variance / Covariance surface",
                      font=dict(size=11),
                      xaxis=dict(type='category'),
                      yaxis=dict(type='category'),
                      plot_bgcolor='#222',
                      paper_bgcolor='#222',
                      font_color='#29E',
                      scene=dict(
                          xaxis=dict(
                              backgroundcolor="#222",
                              gridcolor="white",
                              title="Stock",
                              nticks=50,
                              showbackground=True,
                              zerolinecolor="white", ),
                          yaxis=dict(
                              backgroundcolor="#222",
                              gridcolor="white",
                              title="Stock",
                              nticks=50,
                              showbackground=True,
                              zerolinecolor="white"),
                          zaxis=dict(
                              backgroundcolor="#222",
                              gridcolor="white",
                              title="Variance / Covariance",
                              showbackground=True,
                              zerolinecolor="white", ), ),
                      )

    # fig.update_layout(font_color='#29E')
    return fig

def correlation_heatmap():
    cov = pd.DataFrame(risk.cov)

    cov_hm = df_to_plotly(cov)

    fig = go.Figure(data=go.Heatmap(cov_hm))
    fig.update_layout(autosize=False, width=1270, height=1050, title="Variance / Covariance matrix",
                      plot_bgcolor='#222',
                      paper_bgcolor='#222',
                      font_color='#29E',)
    return fig

def daily_returns(conf_int, days):
    ret = pd.DataFrame(risk.returns)
    r = ret[risk.tickers].fillna(0)
    ret['daily'] = r.dot(risk.weights)*risk.investment
    ret['P&L Date'] =ret.index
    ret['rolling'] = ret['daily'].rolling(days).sum()
    es = -1.0 * ret.sort_values(['rolling'], ascending=True).head(int(len(ret)*conf_int))['rolling'].mean()
    fig = px.bar(ret, x='P&L Date', y="rolling",
                 title="Historical Simulation: 'What-if' " + str(days) + " busness-day returns of current portfolio over the last three years",
                 labels={'daily': str(days) + ' day performance ($USD)'})
    fig.update_layout(autosize=False, width=1100, height=800,
                      plot_bgcolor='#222',
                      paper_bgcolor='#222',
                      font_color='#29E')

    return fig, es

def pnl_histogram(conf_int, days):
    ret = pd.DataFrame(risk.returns)
    r = ret[risk.tickers].fillna(0)
    ret['daily'] = r.dot(risk.weights)*risk.investment

    ret['P & L'] = ret['daily'].rolling(days).sum()
    es = -1.0 * ret.sort_values(['P & L'], ascending=True).head(int(len(ret)*conf_int))['P & L'].mean()
    fig = px.histogram(ret, x=ret['P & L'], marginal='rug', labels={'P & L':'P&L'}, title="Profit & Loss Histogram")
    fig.update_layout(autosize=False, width=1100, height=800,
                      plot_bgcolor='#222',
                      paper_bgcolor='#222',
                      font_color='#29E')
    return fig, es


layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.P("Confidence Level [%]:"),
            dcc.Slider(id="conf-sl", min=0, max=2, marks=conf_dict["display"], value=0, className='dash-bootstrap')
        ], width=2),
        dbc.Col([
            html.P("Period:"),
            dcc.Slider(id="period-sl", min=0, max=2, marks=term_dict["display"], value=0, className='dash-bootstrap')
        ], width={"size": 2, "offset": 0}),
        dbc.Col(dcc.RadioItems(
        id='hist-dd',
        options=[
            {'label': 'Histogram', 'value': 'Histogram'},
            {'label': 'Timeline', 'value': 'Timeline'},
        ],
        value='Histogram'
    )),
        dbc.Col(dcc.RadioItems(
        id='radio-items',
        options=[
            {'label': 'Matrix', 'value': 'Matrix'},
            {'label': 'Surface', 'value': 'Surface'},
        ],
        value='Surface'
    ))
    ]),
    dbc.Row([
        dbc.Col([dbc.Card(
            [
                dbc.CardHeader(html.H5("Risk Metrics: (VaR & ES)")),
                html.Div(id='var-card', children=[]),
            ], color='primary', inverse=True
        ),
        html.Div(dcc.Loading(dcc.Graph(id='hist-bar'), type='graph'))], width=5),
        dbc.Col(dcc.Loading(dcc.Graph(id='cor-surf'), type='graph'), width=7)
    ])
])

@app.callback([Output('var-card', 'children'),
               Output('hist-bar', 'figure')],
              [Input('conf-sl', 'value'),
               Input('period-sl', 'value'),
               Input('hist-dd', 'value')])
def display_risk_metrics(conf, period, hist_bar):
    # See https://www.interviewqs.com/blog/value-at-risk

    term = term_dict["calculate"][period]
    conf_int = conf_dict["calculate"][conf]
    term_d = term_dict["display"][period]
    conf_int_d = conf_dict["display"][conf]
    if hist_bar == "Timeline":
        fig, es = daily_returns(conf_int, term)
    else:
        fig, es = pnl_histogram(conf_int, term)

    var_cutoff = norm.ppf(conf_int, risk.stats['Mean Investment'], risk.stats['Investment Sigma'])
    value_at_risk = (risk.investment - var_cutoff) * np.sqrt(term)

    var_string = str(term_d.replace("_", " ")) + " VaR at " + str(conf_int_d) + "% confidence level is: $" + "{:,}".format(value_at_risk.round(2))
    es_string = str(term_d.replace("_", " ")) + " Expected Shortfall at "+ str(conf_int_d) + "% confidence level is: $" + "{:,}".format(es.round(2))
    return dbc.CardBody([html.H5(var_string), html.H5(es_string)]), fig

@app.callback(Output('cor-surf', 'figure'),
            [Input('radio-items', 'value')])
def show_correlation(v):
    if v == 'Surface':
        fig = correlation_surface()
    else:
        fig = correlation_heatmap()

    return fig
