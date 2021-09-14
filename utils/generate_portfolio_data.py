import yahoo_fin.stock_info as si
from datetime import date, timedelta
import pandas as pd
import pickle
import numpy as np
import pandas_datareader as pdr
from pathlib import Path
import pickle
import os
from pathlib import Path

'''
If you choose to save this project in a folder with a name other then "YT_Dash_Tutorial" then you will
need to make changes to the "if os.getcwd()[-16:] == "YT_Dash_Tutorial":" line below to reflect your
folder name
'''

curr_dir = Path.cwd()
if os.getcwd()[-16:] == "YT_Dash_Tutorial":
    F_PATH = os.path.join(curr_dir, "assets")
else:
    F_PATH = os.path.join(curr_dir.parent, "assets")

'''
Note comment above if you choose a base folder other the "YT_DASH_Tutorial for this project
'''


class PortfolioDataGenerator():
    def __init__(self):
        fname = os.path.join(F_PATH, "Sample Portfolio.xlsx")
        self.df = pd.read_excel(fname)
        self.term_dictionary = {'Yesterday Close': -1, '1 Month': -21, '2 Months': -42, '3 Months': -63, '6 Months': -126, '1 Year': -252, '2 Years': 0, }
        self.quote_dictionary = self.generate_quotes()
        self.performance = self.generate_historical_performance()



    def generate_quotes(self):
        quote_dict = {}
        for ticker in self.df['Ticker'].to_list():
            quote_history = si.get_data(ticker, date.today() - timedelta(days=730), date.today())
            quote_dict[ticker] = quote_history

        return quote_dict

    def generate_historical_performance(self):
        performance_dict = {}
        for ticker, bulk_quotes in self.quote_dictionary.items():
            qty = self.df[self.df['Ticker'] == ticker]['Quantity'].to_list()[0]
            stock_dict = {}
            for column, row_index in self.term_dictionary.items():
                stock_dict[column] = bulk_quotes.iloc[row_index]['adjclose'] * qty
            performance_dict[ticker] = stock_dict

        perf_df = pd.DataFrame(performance_dict).T
        perf_df.index.rename('Ticker', inplace=True)
        composite_df = self.df.merge(perf_df, how='inner', on='Ticker')
        return composite_df

    def write_to_excel(self, fname=""):
        if fname == "":
            fname = os.path.join(F_PATH, "Historical Performance.xlsx")

        self.performance.to_excel(fname)

# port = PortfolioDataGenerator()
# port.write_to_excel()

class BenchmarkGenerator():
    def __init__(self):
        fname=os.path.join(F_PATH, "Sample Portfolio.xlsx")
        self.df = pd.read_excel(fname)
        self.benchmarks = self.get_benchmarks()
        self.term_dictionary = {'1 Month': 27, '2 Months': 54, '3 Months': 81, '6 Months': 162, '1 Year': 314, '2 Years': 628, }
        self.quote_dataframe = self.generate_quotes()
        self.weights = self.get_portfolio_weights()


    def generate_quotes(self):
        i = 0
        tickers = self.df['Ticker'].to_list()
        tickers += self.benchmarks['Ticker'].to_list()
        for ticker in tickers:
            if i == 0:
                i=1
                df = si.get_data(ticker, date.today() - timedelta(days=730), date.today())
                df.rename(columns={'adjclose': ticker}, inplace=True)
                df = df[ticker]

            else:
                df2 = si.get_data(ticker, date.today() - timedelta(days=730), date.today())
                df2.rename(columns={'adjclose': ticker}, inplace=True)
                df2 = df2[ticker]

                df = pd.concat([df, df2], axis=1)

        df = df.interpolate('linear')
        df_daily_pct = df.pct_change()

        return df_daily_pct

    def get_portfolio_weights(self):
        position_dict = {}
        for ticker in self.df['Ticker'].to_list():
            qty = self.df[self.df['Ticker'] == ticker]['Quantity'].to_list()[0]
            price = si.get_live_price(ticker)
            position = qty * price
            position_dict[ticker]=position

        position_df=pd.DataFrame.from_dict(position_dict, orient='index')
        position_df.rename(columns={0: "USD Amount"}, inplace=True)
        total = position_df['USD Amount'].sum()
        position_df['Weight'] = position_df['USD Amount']/total

        return position_df

    def generate_daily_returns(self, term):
        df = self.quote_dataframe.tail(self.term_dictionary[term])

        return df

    def generate_daily_weighted_returns(self, term):
        weights = self.weights['Weight'].to_list()
        bench_weights = np.ones(len(self.benchmarks['Ticker'].to_list())).tolist()
        weights += bench_weights
        return weights * self.generate_daily_returns(term)

    def generate_total_portfolio_return(self, term):
        df = self.generate_daily_weighted_returns(term)
        df_p = df[self.df['Ticker'].to_list()]
        df_b = df[self.benchmarks['Ticker'].to_list()]
        df_b['Portfolio'] = df_p.sum(axis=1)
        return df_b

    def generate_cumulative_portfolio_return(self, term):
        return (1 + self.generate_total_portfolio_return(term)).cumprod()

    def get_benchmarks(self, fname="" ):
        if fname== "":
            fname = os.path.join(F_PATH, 'Benchmarks.xlsx')
        return pd.read_excel(fname)

    def generate_content_for_dropdowns(self):
        types = self.benchmarks['Type'].unique()
        type_dict = {}
        for type in types:
            ticker_list = self.benchmarks[self.benchmarks['Type']==type]['Ticker'].to_list()
            name_list = self.benchmarks[self.benchmarks['Type']==type]['Name'].to_list()
            dropdown_dict = dict(zip(name_list, ticker_list))
            dropdown_list = []
            for k, v in dropdown_dict.items():
                d = {'label': k, 'value': v}
                dropdown_list.append(d)

            type_dict[type] = dropdown_list
        with open(os.path.join(F_PATH, 'dropdown.pickle', 'wb')) as handle:
            pickle.dump(type_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        ticker_dict = self.benchmarks.set_index('Ticker').to_dict()['Name']
        with open(os.path.join(F_PATH, 'ticker.pickle', 'wb')) as handle:
            pickle.dump(ticker_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return type_dict, ticker_dict

    def create_excel_files(self):
        terms = self.term_dictionary
        for term in terms.keys():
            cum_ret = self.generate_cumulative_portfolio_return(term)
            parent = curr_dir.parent
            fname = os.path.join(F_PATH, str(term) + '.xlsx')
            cum_ret.to_excel(fname)


class Risk():
    def __init__(self, filename=""):
        if filename=="":
            filename = os.path.join(F_PATH, 'Sample Portfolio.xlsx')

        self.df = pd.read_excel(filename)

        self.today = date.today()
        self.start = self.today - timedelta(days=3 * 365)
        self.tickers = self.get_tickers()
        self.quotes, self.weights, self.investment = self.get_quotes_and_weights()
        self.returns = self.get_returns()
        self.cov = self.get_covariance()
        self.stats = self.calculate_stats()

    def get_tickers(self):
        return self.df['Ticker'].to_list()


    def get_quotes_and_weights(self):
        quotes = pdr.get_data_yahoo(self.tickers, self.start, self.today)['Adj Close']
        qty = np.array(self.df['Quantity'])
        latest = quotes.iloc[-1]            # Get the latest quote values as a list
        position = latest.values * qty      # Use broadcasting to get an array of USD position values for each stock
        total = position.sum()              # Get the total USD portfolio value
        weights = position / total          # Obtain the proportion of each stock in the overall portfolio by USD Value

        return quotes, weights, total

    def get_returns(self):
        return self.quotes.pct_change()

    def get_covariance(self):
        return self.returns.cov()

    def calculate_stats(self):
        stats_dict = {}
        stats_dict['Average Returns'] = self.returns.mean()                           # Mean Returns for each stock
        stats_dict['Mean Returns'] = stats_dict['Average Returns'].dot(self.weights)  # mean Returns for whole portfolio
        stats_dict['Portfolio Sigma'] = np.sqrt(self.weights.T.dot(self.cov).dot(self.weights))
        stats_dict['Mean Investment'] = (1 + stats_dict['Mean Returns'])*self.investment
        stats_dict['Investment Sigma'] = self.investment * stats_dict['Portfolio Sigma']

        return stats_dict




# var = Risk()
# print(var.stats)


# bench = BenchmarkGenerator()
# returns = bench.generate_daily_returns('1 Month')
# print(returns)
# mean_daily_returns = returns.mean()
# print(mean_daily_returns)
# cumulative_returns = (1+returns).cumprod()
# print(cumulative_returns)
# print(bench.weights)
# print(bench.weights['Weight'].to_list())
# print(bench.generate_cumulative_portfolio_return())
# bench.get_benchmarks()
# print(bench.generate_content_for_dropdowns())
# quotes = bench.generate_cumulative_benchmark_returns()
# print(quotes, quotes.info())
# cum_ret = bench.merge_returns_with_benchmarks('1 Year')
# print(cum_ret, cum_ret.info())
# bench.generate_content_for_dropdowns()
# bench.create_excel_files()