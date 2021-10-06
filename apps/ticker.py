from app import app
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from utils.sp500 import StockInfo, SP500
from utils.generate_portfolio_data import PortfolioDataGenerator
import dash_daq as daq
import yahoo_fin.stock_info as si
import plotly.graph_objects as go

port = PortfolioDataGenerator('assets/Sample Portfolio.xlsx')
sp500 = SP500()
sp500.unpickle_stocks('utils/sp500.pickle')

layout = html.Div([
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='dd-ticker-ticker', options=port.ticker_name_dict(),
                             value='AAPL', className='dash-bootstrap')),
        dbc.Col(daq.BooleanSwitch(id='bs-ticker-ind-sec', on=False,
                                  color='#0088EE',
                                  label="Sector <-> Industry",
                                  labelPosition='top'))
    ]),
    dbc.Row([
        dbc.CardDeck(id='card-ticker', children=[]

        )
    ])
])
def fill_simple_quote(name, ticker, ccy, live, delta):
    if delta < 0:
        colour = "#EE9900"
        sign = ""
    else:
        colour = "#00AAAA"
        sign = "+"

    return dbc.Card([dbc.CardHeader(html.H3(name, style={'white-space': 'normal'})),
                dbc.CardBody([html.H4(ticker)]),
                dbc.CardBody([dbc.Row([html.H6(ccy), html.H1("{:.2f}".format(live))]),
                dbc.Row([html.H6(ccy, style={'color': colour}), html.H1(sign, style={'color': colour}),
                html.H1("{:.2f}".format(delta), style={'color': colour})])])], style={'width': "18rem"})
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
        colour_dict_up = {"ranges":{"white":[0,start], "cyan":[start,val-5], "blue":[val-5,val+5]}}
        bar = daq.GraduatedBar(
            vertical=True,
            color=colour_dict_up,
            max=100,
            value=val,
            label=t_label,
            labelPosition='top'
        )
    else:
        end = 100 * open_low_spread / hl_spread
        colour_dict_down = {"ranges":{"blue":[val-2, val+2],"orange": [val+2,o], "white":[0, val]}}
        bar = daq.GraduatedBar(
            vertical=True,
            color=colour_dict_down,
            max=100,
            value=o,
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

@app.callback(Output('card-ticker', 'children'),
              [Input('dd-ticker-ticker', 'value'),
               Input('bs-ticker-ind-sec', 'value')])
def load_sec_info(ticker, scope):
    live = si.get_live_price(ticker)
    stock = sp500.stock_dict[ticker]
    open = stock.quotes_dict['today']['open']
    delta = live - open

    card_list = []
    simple_quote = fill_simple_quote(stock.name, stock.ticker, "$", live, delta)

    card_list.append(simple_quote)
    changes = fill_changes(stock.quotes_dict, live)
    card_list.append(changes)
    return card_list