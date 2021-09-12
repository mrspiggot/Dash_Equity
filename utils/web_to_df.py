import pandas as pd
from datetime import date, timedelta
import requests
import pypopulation
import pickle

class WebToDF():
    def __init__(self):
        self.population = self.get_population()
        self.country = self.get_country()
        self.oxcgrt = self.get_oxcgrt()
        self.slider_dict = {'calculate': {0: 0, 1: 2000000, 2: 5000000, 3: 10000000, 4: 20000000, 5: 40000000},
                            'display' : {0: '0', 1: '2,000,000', 2: '5,000,000', 3: '10,000,000', 4: '20,000,000', 5: '40,000,000'}}

    def get_country(self):
        fname = "country_continent.pickle"
        try:
            df = pd.read_pickle(fname)
        except Exception as e:
            print(e)
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "connection": "keep-alive",
                "cookie": "dontShowCookieNotice=TRUE",
                "host": "covidtrackerapi.bsg.ox.ac.uk",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-ch-ua": "Windows",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "cross-site",
                "sec-gpc": "1",
                "dnt": "1",
                "origin": "https://stackoverflow.com",
                "referer": "https://stackoverflow.com/questions/56399462/error-message-10054-when-wescraping-with-requests-module",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            }
            df = pd.read_html('https://statisticstimes.com/geography/countries-by-continents.php')[2]
            df.to_pickle(fname)


        df.rename(columns = {'Country or Area': 'Name', "ISO-alpha3 Code": "ISO-3", "M49 Code": "M49", "Region 1": "Region"}, inplace=True)

        df = df[['Name', 'ISO-3', 'M49', 'Region', 'Continent']]
        df = df.dropna()
        clist = df['ISO-3'].tolist()
        p_list = []
        c_list = []
        for c in clist:
            c_pop = pypopulation.get_population(c)
            if c_pop != None:
                c_list.append(c)
                p_list.append(c_pop)

        p_dict = {'Country': c_list, 'Population': p_list}

        pop_df = pd.DataFrame.from_dict(p_dict)

        df2 = pd.merge(df, pop_df, left_on='ISO-3', right_on='Country')
        df2.dropna(inplace=True)
        return df2

    def save_country(self, filename):
        self.country.to_pickle(filename)

    def load_country(self, filename):
        self.country.read_pickle(filename)

    def get_population(self):
        return pd.read_html('https://worldpopulationreview.com/countries')[0]

    def get_oxcgrt(self):
        today = date.today()
        fname = str(today.year)+str(today.month)+str(today.day)+"_OXCGRT.pickle"
        try:
            df2 = pd.read_pickle(fname)
        except Exception as e:
            print(e)
            df2 = self.get_dataframe_from_url(fname)

        cols = ['confirmed', 'deaths', 'stringency_actual', 'stringency', 'stringency_legacy', 'stringency_legacy_disp']
        df2[cols] = df2[cols].apply(pd.to_numeric, downcast='float', errors='coerce')
        df2 = pd.merge(df2, self.country, left_on='country_code', right_on='ISO-3')
        df2.fillna(0)
        df2 = self.get_daily(df2)
        df2 = self.per_million(df2)
        df2 = self.get_smooth_running_totals(df2)

        return df2

    def get_dataframe_from_url(self, fname):
        start_date = date(2020, 1, 23)
        end_date = date.today() - timedelta(days=16)
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "connection": "keep-alive",
            "cookie": "dontShowCookieNotice=TRUE",
            "host": "covidtrackerapi.bsg.ox.ac.uk",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": "Windows",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "cross-site",
            "sec-gpc": "1",
            "dnt": "1",
            "origin": "https://stackoverflow.com",
            "referer": "https://stackoverflow.com/questions/56399462/error-message-10054-when-wescraping-with-requests-module",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        }

        url = "https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/" \
              + start_date.strftime('%Y-%m-%d') \
              + "/" \
              + end_date.strftime('%Y-%m-%d')
        print(url)
        with requests.Session() as session:
            session.get(url)
            myResponse = session.get(url, headers=headers)

        my_json = myResponse.json()
        ox_dict = my_json['data']

        df = pd.concat({k: pd.DataFrame(v).T for k, v in ox_dict.items()}, axis=0)
        session.close()
        df.to_pickle(fname)
        return df


    def get_daily(self, df):
        df['daily_cases'] = df.groupby(['Country'])['confirmed'].transform(lambda x: x.sub(x.shift()).abs())
        df['daily_deaths'] = df.groupby(['Country'])['deaths'].transform(lambda x: x.sub(x.shift()).abs())
        return df

    def per_million(self, df):
        col_list = ['confirmed','deaths', 'daily_cases', 'daily_deaths']
        for c in col_list:
            new_c = c+'_per_million'
            df[new_c] = 1000000 * df[c] / df['Population']
        return df

    def get_smooth_running_totals(self, df):
        df['Total cases per million'] = df.groupby('Country')['confirmed_per_million'].apply(lambda x: x.rolling(window=7).mean())
        df['Smoothed daily deaths per million'] = df.groupby('Country')['daily_deaths_per_million'].apply(lambda x: x.rolling(window=7).mean())
        df['Smoothed daily cases per million'] = df.groupby('Country')['daily_cases_per_million'].apply(lambda x: x.rolling(window=7).mean())
        df['Total deaths per million'] = df.groupby('Country')['deaths_per_million'].apply(lambda x: x.rolling(window=7).mean())

        return df





