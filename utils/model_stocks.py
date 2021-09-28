import yahoo_fin.stock_info as si
from datetime import date

class Model():
    def __init__(self):
        self.tickers = ['gs', 'jpm', 'msft', 'aapl', 'nvax', 'gme', '3333.HK']
        self.names = ['Goldman Sachs', 'JP Morgan', 'Microsoft', 'Apple', 'Novavax', 'GameStop', 'Evergrande']
        self.ticker_dict = dict(zip(self.tickers, self.names))
        self.today = date.today()
        self.dropdown_options = self.populate_dropdown()
        self.date_dict = {1: 30, 2: 60, 3: 90, 4: 180, 5: 360, 6:720}
    def get_quotes(self, start_date):
        ''' This function takes in a start date in order to get a range of stock quote data. It returns a dictionary,
        the key of the dictionary is the ticker and the value of each element in the dictionary is a dataframe that
        contains the OHLCV data for that ticker from the start date through to today'''
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
        ''' Dash requires a list of dictionaries for labels and values to configure a dropdown list. We have the names
        and tickers as attributes of the Model class we can use this method to build this list of dictionaries'''
        options_list = []
        for ticker, name in self.ticker_dict.items():
            d = {'label': name, 'value': ticker}
            options_list.append(d)
        return options_list