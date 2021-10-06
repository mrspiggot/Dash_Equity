from app import app
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from utils.sp500 import StockInfo, SP500
from utils.generate_portfolio_data import PortfolioDataGenerator
import dash_daq as daq
import yahoo_fin.stock_info as si

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
        dbc.Card(id='card-ticker', children=[]

        )
    ])
])

@app.callback(Output('card-ticker', 'children'),
              [Input('dd-ticker-ticker', 'value'),
               Input('bs-ticker-ind-sec', 'value')])
def load_sec_info(ticker, scope):
    live = si.get_live_price(ticker)
    stock = sp500.stock_dict[ticker]
    open = stock.quotes_dict['today']['open']
    delta = live - open
    if delta < 0:
        colour = "#EE9900"
    else:
        colour = "#00AAAA"
    card_list = [dbc.CardHeader(html.H3(stock.name)),
                dbc.CardBody([html.H4(stock.ticker)]),
                  dbc.CardBody([dbc.Row([html.H6("$"), html.H2("{:.2f}".format(live))]),
                               dbc.Row([html.H6("$"), html.H2("{:.2f}".format(delta), style={'color': colour})])])]

    return card_list