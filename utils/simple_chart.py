import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output
import yahoo_fin.stock_info as si
from datetime import date, timedelta
import plotly.graph_objects as go

app = dash.Dash(__name__)

class StockPrice():
    def __init__(self, ticker):
        self.ticker = ticker

    def get_ohlc(self, days):
        today = date.today()
        start = today - timedelta(days=days)
        df = si.get_data(self.ticker, start_date=start, end_date=today)

        return df



app.layout = html.Div(
    [
        html.H1("Sample Dash app to show numreic input, a text box and a dropdown"),
        html.P("No. of days to plot"),
        dcc.Input(id="numeric", type="number", placeholder="10", value=20),
        html.P("Y axis title"),
        dcc.Input(
            id="text", type="text", placeholder="Stock Price", value="Stock Price",
        ),
        html.P("Choose ticker:"),
        dcc.Dropdown(
            id="dropdown", options=[{'label': "Goldman Sachs", 'value': "GS"},
                                    {"label": "JPMorgan", "value": "JPM"},
                                    {"label": "Microsoft", "value": "MSFT"},
                                    {"label": "Apple", "value": "AAPL"}],
            placeholder="Goldman Sachs", value="GS"
        ),
        html.Hr(),
        dcc.Graph(id="chart-out"),

    ]
)


@app.callback(
    Output("chart-out", "figure"),
    Input("numeric", "value"),
    Input("text", "value"),
    Input("dropdown", "value"),
)
def ohlc_render(days, title, ticker):
    stock = StockPrice(ticker)
    df = stock.get_ohlc(days)

    fig = go.Figure(data=go.Candlestick(x=df.index.values, open=df['open'], high=df['high'],
                                        low=df['low'], close=df['adjclose']))
    fig.update_xaxes(title_text = "Date")
    fig.update_yaxes(title_text = title)

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, port=8029)