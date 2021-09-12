from app import app
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import yahoo_fin.stock_info as si
import plotly.graph_objects as go
from datetime import date, timedelta

class Stocks():
    def __init__(self):
        self.tickers = ['gs', 'jpm', 'msft', 'aapl']
        self.names = ['Goldman Sachs', 'JP Morgan', 'Microsoft', 'Apple']
        self.ticker_dict = dict(zip(self.tickers, self.names))
        self.today = date.today()
        self.dropdown_options = self.populate_dropdown()
        self.date_dict = {1: 30, 2: 60, 3: 90, 4: 180, 5: 360, 6:720}

    def get_quotes(self, start_date):
        ''' This function takes in a start date in order to get a range of stock quote data.
        It returns a dictionary, the key of the dictionary is the ticker and the
        value of each element in the dictionary is a dataframe that contains the OHLCV data
        for that ticker from the start date through to today'''
        quote_dict = {}
        for ticker in self.tickers:
            df = si.get_data(ticker, start_date=start_date, end_date=self.today)
            quote_dict[ticker] = df

        return quote_dict

    def get_daily_returns(self, quotes):
        '''This function takes as an input a dictionary of quotes; the key of each dictionary is a stock ticker,
        the value of each element is a dataframe that contains the OHLCV data for that stock over a period of
        time. The function dictionary with the stock ticker as its key and the OHLCV data transposed into a series of
        the cumulative daily returns for that stock'''

        returns_dict = {}
        for ticker, quote_df in quotes.items():
            daily_returns = quote_df['adjclose'].pct_change()
            cum_daily_returns = (daily_returns+1).cumprod()
            returns_dict[ticker] = cum_daily_returns

        return returns_dict

    def populate_dropdown(self):
        ''' Dash requires a list of dictionaries for labels and values to configure a dropdown list. As we
        have the names and ticker symbols as part of the attricutes of the Stocks class we can use this method
        to build this list of dictionaries'''
        options_list = []
        for ticker, name in self.ticker_dict.items():
            d = {'label': name, 'value': ticker}
            options_list.append(d)

        return options_list

stocks = Stocks()
layout = html.Div([
    dbc.Row([
        dbc.Col(dcc.Dropdown(id='ohlc-dropdown',
                             options=stocks.dropdown_options,
                             value=stocks.tickers[0],
                             className='dash-bootstrap'
            ), width=3,
        ),
        dbc.Col(dcc.Slider(id='date-slider',
                           min=1, max=6, marks={1: '1M', 2: '2M', 3: '3M', 4: '6M', 5: '1Y', 6: '2Y'}, value=3),
                width=3),
        dbc.Col(dcc.Dropdown(id='multi-dropdown', options=stocks.dropdown_options, value=stocks.tickers, multi=True,
                             className='dash-bootstrap'), width=5),
        dbc.Col(dcc.Slider(id='type-slider', min=1, max=2, marks={1: 'Price', 2: 'Returns'}, value=2),
                width=1),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Loading(
                dcc.Graph(id='single-chart'), type='graph'
            ), width=6
        ),
        dbc.Col(
            dcc.Loading(
                dcc.Graph(id='multi-chart'), type='graph'
            ), width=6
        ),
    ])

])
@app.callback(Output('single-chart', 'figure'),
              [Input('ohlc-dropdown', 'value'),
               Input('date-slider', 'value')])
def single_stock_ohlc_chart(ticker, date_range):
    quotes = stocks.get_quotes(stocks.today-timedelta(days=stocks.date_dict[date_range]))
    df = quotes[ticker].iloc[date_range:]

    fig = go.Figure(data=go.Candlestick(x=df.index.values, open=df['open'], high=df['high'], low=df['low'], close=df['adjclose']))
    fig.layout.title=stocks.ticker_dict[ticker] + str(": Stock price")
    fig.update_xaxes(title_text = "Date")
    fig.update_yaxes(title_text = "Stock Price ($)")
    fig.update_layout(font=dict(color='#58C'), height=850, plot_bgcolor='#222', paper_bgcolor='#222')

    return fig

@app.callback(Output('multi-chart', 'figure'),
              [Input('multi-dropdown', 'value'),
               Input('date-slider', 'value'),
               Input('type-slider', 'value')])
def multi_stock_returns_chart(ticker, date_range, price_or_return):
    quotes = stocks.get_quotes(stocks.today-timedelta(days=stocks.date_dict[date_range]))
    returns = stocks.get_daily_returns(quotes)

    fig = go.Figure()

    if price_or_return == 1:
        title = 'Multi Stock Prices'
        y_axis_text = 'Stock Price ($)'
        for stock_ticker, prices in quotes.items():
            if stock_ticker in ticker:
                fig.add_trace(go.Scatter(x=prices.index.values,
                                         y=prices['adjclose'],
                                         name=stocks.ticker_dict[stock_ticker]))
    else:
        title = 'Multi Stock Returns'
        y_axis_text = 'Normalised returns'
        for stock_ticker, daily_returns in returns.items():
            if stock_ticker in ticker:
                fig.add_trace(go.Scatter(x=daily_returns.index.values,
                                     y=daily_returns.values,
                                     name=stocks.ticker_dict[stock_ticker]))

    fig.update_layout(font=dict(color='#58C'), height=850,
                      title=title,
                      xaxis_title='Date',
                      yaxis_title=y_axis_text,
                      plot_bgcolor='#222',
                      paper_bgcolor='#222'
                      )

    return fig

