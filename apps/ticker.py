import numpy as np
import pandas as pd

from app import app
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from utils.sp500_si import StockInfo, SP500
from utils.generate_portfolio_data import PortfolioDataGenerator
import dash_daq as daq
import yahoo_fin.stock_info as si
import plotly.graph_objects as go
from plotly.subplots import make_subplots

port = PortfolioDataGenerator('assets/Sample Portfolio.xlsx')
sp500 = SP500()
sp500.unpickle_stocks('utils/sp500.pickle')

layout = html.Div([
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='dd-ticker-ticker', options=port.ticker_name_dict(),
                             value='AAPL', className='dash-bootstrap'), width={"size":2, "offset": 0}),
        dbc.Col(daq.BooleanSwitch(id='bs-ticker-ind-sec', on=False,
                                  color='#0088EE',
                                  label="Sector <-> Industry",
                                  labelPosition='top'), width=1)
    ]),
    dbc.Row([
        dbc.Col(
            dbc.CardDeck(id='card-ticker', children=[]), width={"offset": 0}
        ),
        dbc.Col(
            dcc.Loading(dcc.Graph(id='pb-bar'), type = 'graph')
        )
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Loading(dcc.Graph(id='peer-candlestick'), type='graph'), width={"offset": 0}
        ),
        dbc.Col(
            dcc.Loading(dcc.Graph(id='pe-bar'), type='graph')
        )
    ])
])
def fill_simple_quote(name, ticker, ccy, live, delta, sec, ind):
    if delta < 0:
        colour = "#EE9900"
        sign = ""
    else:
        colour = "#00AAAA"
        sign = "+"

    return dbc.Card(
            [dbc.CardHeader(html.H3(name, style={'white-space': 'normal'})),
            dbc.CardBody([html.H4(ticker)]),
            dbc.CardBody([dbc.Row([html.H6(ccy), html.H1("{:.2f}".format(live))]),
            dbc.Row([html.H6(ccy, style={'color': colour}), html.H1(sign, style={'color': colour}),
            html.H1("{:.2f}".format(delta), style={'color': colour})])]),
            dbc.CardBody([html.H6(sec)]),
            dbc.CardBody([html.H6(ind)]),
            ],
            style={'width': "18rem"}
            )
def generate_indicator(percent_change):
    f = go.Indicator(mode="delta", value=0, number={'prefix': "$"},
                                 delta={'position': 'top',
                                        'reference': -percent_change,
                                        'valueformat': '.2%',
                                        "font":{"size":16}})
    fig = go.Figure(f)
    fig.layout.height=100
    fig.layout.width=100
    fig.layout.plot_bgcolor='#313131'
    fig.layout.paper_bgcolor='#313131'

    return fig
def fill_change_bar(quote, live, t_label):
    h = quote['high']
    l = quote['low']
    o = quote ['open']
    if o > h:
        h=o
    if o < l:
        l=o
    if live > h:
        h=live
    if live < l:
        l=live
    hl_spread = h - l
    now_low_spread = live - l
    open_low_spread = o - l
    val = int(100*now_low_spread/hl_spread)
    if live > o:
        start = 100*open_low_spread/hl_spread
        colour_dict_up = {"ranges":{"cyan":[start,val-1], "blue":[val-1,val+1], "gray":[0,100]}}
        bar = daq.GraduatedBar(
            vertical=True,
            color=colour_dict_up,
            max=100,
            # value=val,
            value=100,
            label=t_label,
            labelPosition='top',
        )
    else:
        end = 100 * open_low_spread / hl_spread
        colour_dict_down = {"ranges":{"blue":[val-1, val+1],"orange": [val+1,o], "gray":[0, 100]}}
        bar = daq.GraduatedBar(
            vertical=True,
            color=colour_dict_down,
            max=100,
            # value=o,
            value=100,
            label=t_label,
            labelPosition='top'
        )

    return bar

def fill_changes(quote, live):
    open_today = quote['today']['open']
    open_month = quote['month']['open']
    open_year = quote['year']['open']

    dcp = (live-open_today)/open_today
    mcp = (live-open_month)/open_month
    ycp = (live-open_year)/open_year

    fig_day = generate_indicator(dcp)
    fig_mth = generate_indicator(mcp)
    fig_yr = generate_indicator(ycp)

    day = fill_change_bar(quote['today'], live, "Day change")
    month = fill_change_bar(quote['month'], live, "Month change")
    year = fill_change_bar(quote['year'], live, "Year change")

    dg = dcc.Graph(id='day-ind', figure=fig_day)
    mg = dcc.Graph(id='mth-ind', figure=fig_mth)
    yg = dcc.Graph(id='yr-ind', figure=fig_yr)

    day_col = dbc.Col([dg, day])
    month_col = dbc.Col([mg, month])
    year_col = dbc.Col([yg, year])

    change_card = dbc.Card([
        dbc.CardHeader(html.H4("Day, Month, Year OHL-Live Prices")),
        dbc.CardBody(dbc.Row([day_col, month_col, year_col], style={"white-space": "nowrap"}))],
        style={'width': "36rem"}
    )
    return change_card
def fill_psar_bar(psar_dict, quotes, live):


    t = psar_dict['t']
    t_1 = psar_dict['t-1']
    max_p = max(t_1, t)

    if psar_dict['t'] > live:
        max_p = max(t_1, t)
        trend = "DOWN"
        colour = "#EE9900"
        l = quotes['low']
        hl = max_p - l

        pt = 100 * (t-l)/hl
        pt_1 = 100 * (t_1-l)/hl
        plive = 100 * (live - l)/hl
        po = 100 * (quotes['open'] - l)/hl


        if live > quotes['open']:
            colour_dict = {"ranges": {"#000": [0, 2],
                                      "red": [pt - 1, pt + 1],
                                      "orange": [pt + 1, pt_1],
                                      "blue": [plive - 2, plive + 2],
                                      "cyan": [po, plive-2],
                                      "#000001": [98, 101],
                                      "#555555": [2, 98]}}
        else:
            colour_dict = {"ranges": {"#000": [0, 2],
                                      "red": [pt - 1, pt + 1],
                                      "orange": [pt + 1, pt_1],
                                      "blue": [plive - 2, plive + 2],
                                      "#EE9900": [plive+2, po],
                                      "#000001": [98, 101],
                                      "#555555": [2, 98]}}


    else:
        min_p = min(t_1, t)
        trend = "UP"
        colour = "#00AAAA"
        h = quotes['high']
        hl = h - min_p
        l = min_p

        pt = 100 * (t-l)/hl
        pt_1 = 100 * (t_1-l)/hl
        plive = 100 * (live - l)/hl
        po = 100 * (quotes['open'] - l)/hl

        if live > quotes['open']:
            colour_dict = {"ranges": {"#000": [0, 2],
                                      "red": [pt - 1, pt + 1],
                                      "orange": [pt + 1, pt_1],
                                      "blue": [plive - 2, plive + 2],
                                      "cyan": [po, plive-2],
                                      "#000001": [98, 101],
                                      "#555555": [2, 98]}}
        else:
            colour_dict = {"ranges": {"#000": [0, 2],
                                      "red": [pt - 1, pt + 1],
                                      "orange": [pt + 1, pt_1],
                                      "blue": [plive - 2, plive + 2],
                                      "#EE9900": [plive+2, po],
                                      "#000001": [98, 101],
                                      "#555555": [2, 98]}}



    bar = daq.GraduatedBar(
        vertical=True,
        color=colour_dict,
        max=100,
        value=100,
        labelPosition='top',
    )
    return bar, trend, colour



def fill_bb_bar(bb_dict, live):

    h = bb_dict['last value']['high']
    l = bb_dict['last value']['low']
    t_1 = bb_dict['last value']['t-1 mavg']
    t = bb_dict['last value']['moving average']
    hl = h-l

    pt = 100 * (t - l)/hl
    pt_1 = 100 * (t_1 - l)/hl
    plive = 100 * (live-l)/hl

    if t_1 > t:
        colour_dict = {"ranges":{"#000": [0,2],
                                 "red":[pt-1,pt+1],
                                 "orange": [pt+1, pt_1],
                                 "blue": [plive-2, plive+2],
                                 "#000001": [98, 101],
                                 "#555555":[2,98]}}
    else:
        colour_dict = {"ranges":{"#000": [0,2],
                                 "red":[pt-1,pt+1],
                                 "cyan": [pt_1, pt-1],
                                 "blue": [48, 52],
                                 "#000001": [98, 101],
                                 "#555555":[2,98]}}


    bar = daq.GraduatedBar(
        vertical=True,
        color=colour_dict,
        max=100,
        value=100,
        labelPosition='top',
    )
    return bar

def fill_ti(stock, live):
    bb_dict = stock.bb
    psar_dict = stock.psar
    stoch_dict = stock.stochastic

    bb_bar = fill_bb_bar(bb_dict, live)
    label_text = html.P(["Bolinger Bands (20/2)",  html.Br(), "High: ", "{:.2f}".format(bb_dict['last value']['high']),
                         html.Br(), "Low: ", "{:.2f}".format(bb_dict['last value']['low']),
                         html.Br(), "MA(t): ", "{:.2f}".format(bb_dict['last value']['moving average']),
                         html.Br(), "MA(t-1): ", "{:.2f}".format(bb_dict['last value']['t-1 mavg'])])
    bb_comp = dbc.Col([label_text, bb_bar], align='center')
    psar_bar, trend, colour = fill_psar_bar(psar_dict, stock.quotes_dict['today'], live)
    label_text = html.H4(["PSAR", html.Br(), "(0.02/0.22)"])
    trend_text = html.H1([trend, html.Br()], style={'color': colour})
    psar_comp = dbc.Col([label_text, trend_text, psar_bar])

    ti_card = dbc.Card([
        dbc.CardHeader(html.H4("Technical Indicators")),
        dbc.CardBody(dbc.Row([bb_comp, psar_comp]))
    ],
    style={'width': "36rem"})

    return ti_card

def peer_candlestick(stock, scope):

    if scope == 0:
        peer_tickers = stock.industry_peers
    else:
        peer_tickers = stock.sector_peers

    f_list = []
    t_list = []
    for ticker in peer_tickers:
        s_d = {}
        f_d = {}

        s = sp500.stock_dict[ticker]
        live = si.get_live_price(ticker)
        t = s.ohlcv.tail(1)

        th = t['high'].to_list()[0]
        tl = min(t['low'].to_list()[0], live)
        to = t['open'].to_list()[0]
        tc = live

        ph = 100 * (th-to)/to
        pl = 100 * (tl-to)/to
        po = 0
        pc = 100 * (tc-to)/to

        f_d['P/E'] = s.fundamentals['Fwd P/E']
        f_d['P/B'] = s.fundamentals['P/B']
        f_d['ticker'] = ticker

        s_d['high'] = ph
        s_d['low'] = pl
        s_d['open'] = po
        s_d['close'] = pc
        s_d['ticker'] = ticker

        t_list.append(s_d)
        f_list.append((f_d))

    df = pd.DataFrame(t_list)
    dff = pd.DataFrame(f_list)
    dff['colour'] = 'cyan'
    dff['colour'][dff['ticker']==stock.ticker] = 'orange'
    df.to_excel(stock.ticker+"_DF.xlsx")
    df.sort_values(by=['close'], ascending=False, inplace=True)

    dff.sort_values(by=['P/E'], ascending=False, inplace=True)

    tstring = stock.ticker + " P/E = " + "{:.2f}".format(dff['P/E'][dff['ticker']==stock.ticker].to_list()[0])
    fig_pe = go.Figure(go.Bar(
        x=dff['ticker'],
        y=dff['P/E'],
        marker={'color': dff['colour']},

    ))
    fig_pe.update_layout(font=dict(color='#58C'),
                         height=650, width=1200,
                         plot_bgcolor='#222',
                         paper_bgcolor='#222',
                         # scene=dict(xaxis=dict(nticks=50)),
                         title={'text':tstring})
    fig_pe.update_yaxes(title_text = "PE Ratio")

    dff.sort_values(by=['P/B'], ascending=False, inplace=True)
    tstring = stock.ticker + " P/B = " + "{:.2f}".format(dff['P/B'][dff['ticker']==stock.ticker].to_list()[0])
    fig_pb = go.Figure(go.Bar(
        x=dff['ticker'],
        y=dff['P/B'],
        marker={'color': dff['colour']},

    ))
    fig_pb.update_layout(font=dict(color='#58C'),
                         height=530, width=1200,
                         plot_bgcolor='#222',
                         paper_bgcolor='#222',
                         title={'text':tstring})
    fig_pb.update_yaxes(title_text = "Price to Book Ratio")

    fig = go.Figure(go.Candlestick(
        x=df['ticker'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    ))
    fig.update_layout(xaxis_rangeslider_visible=False)
    fig['layout']['yaxis']['showgrid'] = False
    fig.update_layout(font=dict(color='#58C'), height=650, width=1500, plot_bgcolor='#222', paper_bgcolor='#222')
    fig.update_yaxes(title_text = "Percentage change from open")
    fig.add_annotation(x=stock.ticker, y=df['high'].max(), text=stock.ticker, font=dict(size=22), ax=0,
        bordercolor="#c7c7c7", borderwidth=2, borderpad=4, bgcolor="#ff7f0e")

    return fig, fig_pe, fig_pb


@app.callback([Output('card-ticker', 'children'),
               Output('peer-candlestick', 'figure'),
               Output('pe-bar', 'figure'),
               Output('pb-bar', 'figure')],
              [Input('dd-ticker-ticker', 'value'),
               Input('bs-ticker-ind-sec', 'on')])
def load_sec_info(ticker, scope):
    live = si.get_live_price(ticker)
    stock = sp500.stock_dict[ticker]
    open = stock.quotes_dict['today']['open']
    delta = live - open

    card_list = []
    simple_quote = fill_simple_quote(stock.name, stock.ticker, "$", live, delta, stock.sector, stock.industry)

    card_list.append(simple_quote)
    changes = fill_changes(stock.quotes_dict, live)
    card_list.append(changes)
    technical_indicators = fill_ti(stock, live)
    card_list.append(technical_indicators)
    fig, fig_pe, fig_pb = peer_candlestick(stock, scope)

    return card_list, fig, fig_pe, fig_pb