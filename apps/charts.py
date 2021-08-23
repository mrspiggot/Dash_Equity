from app import app
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import yahoo_fin.stock_info as si
from datetime import date
import pandas as pd


class Stocks():
    def __init__(self):
        self.tickers = ['gs', 'jpm', 'msft', 'aapl']
        self.names = ['Goldman Sachs', 'JP Morgan', 'Microsoft', 'Apple']
        self.ticker_dict = zip(self.tickers, self.names)
        self.today = date.today()

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

