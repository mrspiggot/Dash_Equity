import numpy as np
import yahoo_fin.stock_info as si
from datetime import date, timedelta, datetime
from ta.volatility import BollingerBands
from ta.utils import dropna
from ta.trend import PSARIndicator
from ta.momentum import StochasticOscillator
import math
import pandas as pd
import pickle
import os
from pandas_datareader import data as pdr

# from utils.generate_portfolio_data import PortfolioDataGenerator


class StockInfo():
    def __init__(self, ticker):
        today = date.today()
        one_year = today - timedelta(days=365)
        sp_500 = si.tickers_sp500(True)


        self.data = si.get_quote_data(ticker)
        self.ticker = ticker
        # self.ohlcv = si.get_data(ticker, start_date=one_year, end_date=today)
        self.ohlcv = self.pandas_yahoo(ticker, one_year, today)
        self.sector = sp_500[sp_500['Symbol'] == ticker]['GICS Sector'].to_list()[0]
        self.industry = sp_500[sp_500['Symbol'] == ticker]['GICS Sub-Industry'].to_list()[0]
        self.name = sp_500[sp_500['Symbol'] == ticker]['Security'].to_list()[0]
        self.quotes_dict = self.fill_quotes_dict()
        self.bb = self.fill_bollinger_bands()
        self.psar = self.fill_psar()
        self.stochastic = self.fill_stoch()
        self.liquidity = self.fill_liquidity()
        self.industry_peers = sp_500[sp_500['GICS Sub-Industry'] == self.industry]['Symbol'].to_list()
        self.sector_peers = sp_500[sp_500['GICS Sector'] == self.sector]['Symbol'].to_list()


        print(self.data)
        self.fundamentals = self.get_fundamentals()

    def pandas_yahoo(self, ticker, start, end):
        df = pdr.get_data_yahoo(ticker, start, end)
        df.set_axis(['high', 'low', 'open', 'close', 'volume', 'adjclose'], axis=1, inplace=True)
        print(df)
        return df

    def fill_quotes_dict(self):
        quotes_dict = {}
        today = {}
        month = {}
        year = {}

        try:
            today['open'] = self.data['regularMarketPreviousClose']
        except Exception as e:
            today['open'] = self.ohlcv.tail(1)['adjclose']
        try:
            today['high'] = self.data['regularMarketDayHigh']
        except Exception as e:
            today['high'] = self.ohlcv.tail(1)['high']
        try:
            today['low'] = self.data['regularMarketDayLow']
        except Exception as e:
            today['low'] = self.ohlcv.tail(1)['low']

        year['high'] = self.data['fiftyTwoWeekHigh']
        year['low'] = self.data['fiftyTwoWeekLow']
        year['open'] = self.ohlcv.iloc[0]['adjclose']

        trailing_month = self.ohlcv.tail(21)
        month['high'] = trailing_month['adjclose'].max()
        month['low'] = trailing_month['adjclose'].min()
        month['open'] = trailing_month.iloc[0]['adjclose']
        if month['open'] != month['open']:
            month['open'] = trailing_month.iloc[1]['adjclose']
            print(trailing_month.iloc[0])
            print(trailing_month.iloc[1])
            print(trailing_month, trailing_month.info())

        quotes_dict['today'] = today
        quotes_dict['month'] = month
        quotes_dict['year'] = year

        return quotes_dict

    def fill_bollinger_bands(self):
        bb_dict = {}
        bb_chart = {}
        last_value = {}

        bb_df = dropna(self.ohlcv)

        bb = BollingerBands(bb_df['adjclose'], window=20, window_dev=2)

        bb_chart['moving average'] = bb.bollinger_mavg()
        bb_chart['high'] = bb.bollinger_hband()
        bb_chart['low'] = bb.bollinger_lband()

        last_value['moving average'] = bb_chart['moving average'].tail(1).to_list()[0]
        last_value['high'] = bb_chart['high'].tail(1).to_list()[0]
        last_value['low'] = bb_chart['low'].tail(1).to_list()[0]

        bb_chart['t-1 mavg'] = bb_chart['moving average'].drop(bb_chart['moving average'].tail(1).index)
        last_value['t-1 mavg'] = bb_chart['t-1 mavg'].tail(1).to_list()[0]

        bb_dict['chart'] = bb_chart
        bb_dict['last value'] = last_value

        return bb_dict

    def fill_psar(self):
        p_dict = {}

        psar = PSARIndicator(self.ohlcv['high'], self.ohlcv['low'], self.ohlcv['close'], step=0.02, max_step=0.2)

        u = psar.psar_up()
        d = psar.psar_down()

        ul = u.tail(2).to_list()
        dl = d.tail(2).to_list()

        if ul[1] != ul[1]:
            p_dict['direction'] = 'DOWN'
            p_dict['t'] = dl[1]
            if ul[0] != ul[0]:
                p_dict['t-1'] = dl[0]
            else:
                p_dict['t-1'] = dl[1]

        if dl[1] != dl[1]:
            p_dict['direction'] = 'UP'
            p_dict['t'] = ul[1]
            if dl[0] != dl[0]:
                p_dict['t-1'] = ul[0]
            else:
                p_dict['t-1'] = ul[1]

        return p_dict

    def fill_stoch(self):
        stoch_dict = {}
        fast = {}
        slow_d = {}

        stoch=StochasticOscillator(self.ohlcv['high'], self.ohlcv['low'], self.ohlcv['close'], window=15, smooth_window=5)
        raw=stoch.stoch().tail(2).to_list()
        signal=stoch.stoch_signal()
        slow = signal.rolling(3).mean().tail(2).to_list()
        signal = signal.tail(2).to_list()

        if signal[1] > 80:
            fast['trade'] = "SELL"
        elif signal[1] < 20:
            fast['trade'] = "BUY"
        else:
            fast['trade'] = "HOLD"

        if slow[1] > 80:
            slow_d['trade'] = "SELL"
        elif slow[1] < 20:
            slow_d['trade'] = "BUY"
        else:
            slow_d['trade'] = "HOLD"

        fast['15 t-1'] = raw[0]
        fast['15 t'] = raw[1]
        fast['5 t-1'] = signal[0]
        fast['5 t'] = signal[1]

        slow_d['5 t-1'] = signal[0]
        slow_d['5 t'] = signal[1]
        slow_d['3 t-1'] = slow[0]
        slow_d['3 t'] = slow[1]

        stoch_dict['fast'] = fast
        stoch_dict['slow'] = slow_d

        return stoch_dict

    def fill_liquidity(self):
        liquidity = {}

        liquidity['vol'] = self.ohlcv.tail(1)['volume'].to_list()[0]
        liquidity['avg vol'] = self.ohlcv['volume'].mean()
        liquidity['bid'] = self.data['bid']
        liquidity['ask'] = self.data['ask']

        liquidity['bidsize'] = self.data['bidSize']
        liquidity['asksize'] = self.data['askSize']

        try:
            liquidity['bid ask spread'] = self.ohlcv.tail(1)['open'].to_list()[0] * (
                        liquidity['ask'] / liquidity['bid'] - 1)
        except Exception as e:
            liquidity['bid ask spread'] = 0.05

        return liquidity

    def millify(self, n):
        millnames = ['', ' k', ' MM', ' Bn', ' Trn']
        n = float(n)
        millidx = max(0, min(len(millnames) - 1,
                             int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

        return '{:.2f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])

    def get_fundamentals(self):
        fundamentals = {}

        try:
            fundamentals['Name'] = self.data['longName']
        except Exception as e:
            fundamentals['Name'] = self.ticker

        try:
            fundamentals['CCY'] = self.data['currency']
        except Exception as e:
            fundamentals['CCY'] = 'USD'

        try:
            fundamentals['Div rate'] = self.data['trailingAnnualDividendRate']
        except Exception as e:
            fundamentals['Div rate'] = 0.0
        try:
            fundamentals['Div yield'] = self.data['trailingAnnualDividendYield']
        except Exception as e:
            fundamentals['Div yield'] = 0.0
        try:
            fundamentals['Fwd P/E'] = self.data['forwardPE']
        except Exception as e:
            fundamentals['Fwd P/E'] = 0.0
        try:
            fundamentals['P/E ttm'] = self.data['trailingPE']
        except Exception as e:
            fundamentals['P/E ttm'] = fundamentals['Fwd P/E']

        try:
            fundamentals['Float'] = self.millify(self.data['sharesOutstanding'])
        except Exception as e:
            fundamentals['Float'] = 0

        try:
            fundamentals['Book Value'] = self.data['bookValue']
        except Exception as e:
            fundamentals['Book Value'] = 0.0

        try:
            fundamentals['Market Cap'] = self.millify(self.data['marketCap'])
            fundamentals['mkt cap int'] = self.data['marketCap']
        except Exception as e:
            fundamentals['Market Cap'] = 0
            fundamentals['mkt cap int'] = 0

        try:
            fundamentals['P/B'] = self.data['priceToBook']
        except Exception as e:
            fundamentals['P/B'] = 0.0


        try:
            fundamentals['Beta'] = si.get_quote_table(self.ticker)['Beta (5Y Monthly)']
        except Exception as e:
            fundamentals['Beta'] = 1.0

        return fundamentals


class SP500():
    def __init__(self, fname='../assets/Sample Portfolio.xlsx'):
        self.tickers = si.tickers_sp500()
        self.ticker_data = si.tickers_sp500(True)
        self.stock_dict = {}
        self.sector_average = pd.DataFrame()
        self.industry_average = pd.DataFrame()

    def populate_stock_info(self):
        for ticker in self.tickers:
            print(ticker)
            try:
                self.stock_dict[ticker] = StockInfo(ticker)
            except Exception as e:
                print(e, "Unable to get info for", ticker)
                self.stock_dict[ticker] = {}

            pickle.dump(self.stock_dict[ticker], open("../assets/stock_info/"+str(ticker)+".pickle", "wb"))

    def pickle_stocks(self, filename="sp500.pickle"):
        pickle.dump(self.stock_dict, open(filename, "wb"))

    def unpickle_stocks(self, filename="sp500.pickle"):
        print(filename)
        print(os.getcwd())
        self.stock_dict = pickle.load(open(filename, "rb"))

    def get_sector_averages(self):
        sector_list = self.ticker_data['GICS Sector'].unique()
        company_data_list = []
        for sector in sector_list:
            ticker_list = self.ticker_data[self.ticker_data['GICS Sector'] == sector]['Symbol'].to_list()

            for ticker in ticker_list:
                fundamentals = self.stock_dict[ticker].fundamentals
                fundamentals['sector'] = sector
                company_data_list.append(fundamentals)

        df = pd.DataFrame(company_data_list)
        self.sector_average = pd.pivot_table(df,
                                 values=['Div rate', 'Div yield', 'Fwd P/E', 'P/E ttm', 'Book Value', 'mkt cap int', 'P/B', 'Beta'],
                                 index='sector',
                                 aggfunc={'Div rate': np.mean,
                                          'Div yield': np.mean,
                                          'Fwd P/E': np.mean,
                                          'P/E ttm': np.mean,
                                          'Book Value': np.mean,
                                          'mkt cap int': np.mean,
                                          'P/B': np.mean,
                                          'Beta': np.mean,
                                          })


    def get_industry_averages(self):
        industry_list = self.ticker_data['GICS Sub-Industry'].unique()
        print(industry_list)
        company_data_list = []
        for industry in industry_list:
            ticker_list = self.ticker_data[self.ticker_data['GICS Sub-Industry'] == industry]['Symbol'].to_list()

            for ticker in ticker_list:
                fundamentals = self.stock_dict[ticker].fundamentals
                fundamentals['industry'] = industry
                company_data_list.append(fundamentals)

        df = pd.DataFrame(company_data_list)
        self.industry_average = pd.pivot_table(df,
                                 values=['Div rate', 'Div yield', 'Fwd P/E', 'P/E ttm', 'Book Value', 'mkt cap int', 'P/B', 'Beta'],
                                 index='industry',
                                 aggfunc={'Div rate': np.mean,
                                          'Div yield': np.mean,
                                          'Fwd P/E': np.mean,
                                          'P/E ttm': np.mean,
                                          'Book Value': np.mean,
                                          'mkt cap int': np.mean,
                                          'P/B': np.mean,
                                          'Beta': np.mean,
                                          })




# sp500 = SP500()
# sp500.populate_stock_info()
# sp500.pickle_stocks()
# print(sp500.get_industry_averages())
# print(sp500.get_sector_averages())
# print("Finished", datetime.now())
# print(sp500.sector_average, sp500.sector_average.info())


