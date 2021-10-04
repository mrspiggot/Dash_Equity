import yahoo_fin.stock_info as si
from datetime import date, timedelta
from ta.volatility import BollingerBands
from ta.utils import dropna
from ta.trend import PSARIndicator
from ta.momentum import StochasticOscillator
import math
import pandas as pd


class StockInfo():
    def __init__(self, ticker):
        today = date.today()
        one_year = today - timedelta(days=365)
        sp_500 = si.tickers_sp500(True)

        self.data = si.get_quote_data(ticker)
        self.ticker = ticker
        self.ohlcv = si.get_data(ticker, start_date=one_year, end_date=today)
        self.sector = sp_500[sp_500['Symbol'] == ticker]['GICS Sector'].to_list()[0]
        self.industry = sp_500[sp_500['Symbol'] == ticker]['GICS Sub-Industry'].to_list()[0]
        self.name = sp_500[sp_500['Symbol'] == ticker]['Security'].to_list()[0]
        self.quotes_dict = self.fill_quotes_dict()
        self.bb = self.fill_bollinger_bands()
        self.psar = self.fill_psar()
        self.stochastic = self.fill_stoch()
        self.liquidity = self.fill_liquidity()
        self.peers = sp_500[sp_500['GICS Sub-Industry'] == self.industry]['Symbol'].to_list()
        self.fundamentals = self.get_fundamentals()



    def fill_quotes_dict(self):
        quotes_dict = {}
        today = {}
        month = {}
        year = {}

        today['open'] = self.data['regularMarketPreviousClose']
        today['high'] = self.data['regularMarketDayHigh']
        today['low'] = self.data['regularMarketDayLow']

        year['high'] = self.data['fiftyTwoWeekHigh']
        year['low'] = self.data['fiftyTwoWeekLow']
        year['open'] = self.ohlcv.iloc[0]['adjclose']

        trailing_month = self.ohlcv.tail(21)
        month['high'] = trailing_month['adjclose'].max()
        month['low'] = trailing_month['adjclose'].min()
        month['open'] = trailing_month.iloc[0]['adjclose']

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
        liquidity['avg_vol'] = self.millify(self.data['averageDailyVolume3Month'])
        liquidity['bid'] = self.data['bid']
        liquidity['ask'] = self.data['ask']
        liquidity['bid ask spread'] = self.ohlcv.tail(1)['open'].to_list()[0] * (liquidity['ask'] / liquidity['bid'] - 1)
        liquidity['bidsize'] = self.data['bidSize']
        liquidity['asksize'] = self.data['askSize']

        return liquidity

    def millify(self, n):
        millnames = ['', ' k', ' MM', ' Bn', ' Trn']
        n = float(n)
        millidx = max(0, min(len(millnames) - 1,
                             int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

        return '{:.2f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])

    def get_fundamentals(self):
        fundamentals = {}

        fundamentals['Name'] = self.data['longName']
        fundamentals['CCY'] = self.data['currency']
        fundamentals['Div rate'] = self.data['trailingAnnualDividendRate']
        fundamentals['Div yield'] = self.data['trailingAnnualDividendYield']
        fundamentals['P/E ttm'] = self.data['trailingPE']
        fundamentals['Float'] = self.millify(self.data['sharesOutstanding'])
        fundamentals['Book Value'] = self.data['bookValue']
        fundamentals['Market Cap'] = self.millify(self.data['marketCap'])
        fundamentals['mkt cap int'] = self.data['marketCap']
        fundamentals['Fwd P/E'] = self.data['forwardPE']
        fundamentals['P/B'] = self.data['priceToBook']
        fundamentals['Avg Rating'] = self.data['averageAnalystRating']
        fundamentals['Beta'] = si.get_quote_table(self.ticker)['Beta (5Y Monthly)']

        return fundamentals


class SP500():
    def __init__(self):
        tickers = si.tickers_sp500(True)


aapl = StockInfo('AAPL')
print(aapl.liquidity)
print(aapl.fundamentals)
print(aapl.data)

