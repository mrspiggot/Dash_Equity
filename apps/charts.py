from app import app
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
from datetime import timedelta
from utils.model_stocks import Model
from plotly.subplots import make_subplots

stocks = Model()
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
        dbc.Col(dcc.Dropdown(id='multi-dropdown', options=stocks.dropdown_options, value=['gs', 'jpm', 'msft', 'aapl'], multi=True,
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

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Candlestick(x=df.index.values, open=df['open'], high=df['high'], low=df['low'],
                                      close=df['adjclose'], name="OHLC Prices"),
        secondary_y=False,

    )
    fig.add_trace(
        go.Scatter(x=df.index.values, y=df['volume'], name="Volume", line_color='#05B', line_dash='dash'),
        secondary_y=True,
    )
    fig['layout']['yaxis2']['showgrid'] = False
    fig.layout.title=stocks.ticker_dict[ticker] + str(": Stock price")
    fig.update_xaxes(title_text = "Date")
    fig.update_yaxes(title_text = "Stock Price ($)", secondary_y=False)
    fig.update_yaxes(title_text = "Daily Volume", secondary_y=True)
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
                fig.add_trace(go.Scatter(x=prices.index.values, y=prices['adjclose'], name=stocks.ticker_dict[stock_ticker]))
    else:
        title = 'Multi Stock Returns'
        y_axis_text = 'Normalised returns'
        for stock_ticker, daily_returns in returns.items():
            if stock_ticker in ticker:
                fig.add_trace(go.Scatter(x=daily_returns.index.values, y=daily_returns.values, name=stocks.ticker_dict[stock_ticker]))

    fig.update_layout(font=dict(color='#58C'), height=850, title=title, xaxis_title='Date', yaxis_title=y_axis_text,
                      plot_bgcolor='#222', paper_bgcolor='#222')

    return fig

