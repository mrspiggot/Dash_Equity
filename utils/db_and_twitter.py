from decouple import config
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import sqlite3
import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from unidecode import unidecode
import json
import pprint
import time





class DB_SQLite():
    def __init__(self, dbname="twitter.db"):
        self.conn = sqlite3.connect(dbname)
        self.c = self.conn.cursor()

    def create_table(self, table_name, columns_and_types):
        '''This method will create a table "table_name" using the dictionary "columns_and_types" for the names
        and types of each column'''

        index_list = []
        index_1 = "CREATE INDEX IF NOT EXISTS fast_"
        index_2 = " ON "
        create_table_string = "CREATE TABLE IF NOT EXISTS " + str(table_name) + "("
        for my_col, my_type in columns_and_types.items():
            create_table_string += my_col + " " + my_type + ", "
            index_string = index_1 + my_col + index_2 + table_name + "(" + my_col + ")"
            index_list.append(index_string)

        size = len(create_table_string)
        create_table_string = create_table_string[:size -2] + ")"

        self.c.execute(create_table_string)
        for col_index in index_list:
            self.c.execute(col_index)

        self.conn.commit()

    def insert_values(self, table_name, cols_and_values):
        '''This method will insert a dictionary of "cols_and_values", which contain the column name and associated value,
         into a table named "table_name" it will not perform type checking '''
        insert_string = "INSERT INTO " + str(table_name) + " ("
        insert_location = "("
        insert_values = []
        for col, val in cols_and_values.items():
            insert_string += str(col) + ", "
            insert_values.append(val)
            insert_location += '?, '

        size_location = len(insert_location)
        insert_location = insert_location[:size_location -2] + ")"
        size_string = len(insert_string)
        insert_string = insert_string[:size_string -2] + ") VALUES " + insert_location
        variables_tuple = tuple(insert_values)

        self.c.execute(insert_string, variables_tuple)
        self.conn.commit()

    def close_cursor(self):
        self.c.close()

    def close_connection(self):
        self.conn.close()

    def sql_to_df(self, sql_string):
        return pd.read_sql_query(sql_string, self.conn)





class listener(StreamListener):
    def __init__(self, db_conn, tl):
        self.my_conn = db_conn
        self.analyzer = SentimentIntensityAnalyzer()
        self.track_list=tl

    def on_data(self, data):
        try:
            data = json.loads(data)
            # pprint.pp(data)
            tweet = unidecode(data['text'])
            time_ms = data['timestamp_ms']
            vs = self.analyzer.polarity_scores(tweet)
            analysis = TextBlob(tweet)
            # print(time_ms, tweet, vs['neg'], vs['neu'], vs['pos'], vs['compound'], analysis.sentiment[0])
            ins_dict = {}
            for srch in self.track_list:
                if srch in tweet:
                    ins_dict['keyword'] = srch
                    ins_dict['unix_time'] = time_ms
                    ins_dict['tweet'] = tweet
                    ins_dict['neg'] = vs['neg']
                    ins_dict['neu'] = vs['neu']
                    ins_dict['pos'] = vs['pos']
                    ins_dict['compound'] = vs['compound']
                    ins_dict['polarity'] = analysis.sentiment[0]
                    ins_dict['subjectivity'] = analysis.sentiment[1]
                    self.my_conn.insert_values("tweet_sentiment", ins_dict)


        except KeyError as e:
            print(str(e))
        return(True)

    def on_error(self, status):
        print(status)


class TwitterClient():
    def __init__(self, tweet_dict={'entertainment': ['Drake', 'ABBA', 'Kanye', 'Kardashian'], 'crypto': ['BTC', 'ADA', 'ETH', 'XRP', "LTC", "DOGE"], 'politics': ['Trump', 'Biden', 'Covid', 'Afghanistan', 'Brexit']}):
        CONSUMER_KEY = config('CONSUMER_KEY')
        CONSUMER_SECRET = config('CONSUMER_SECRET')
        ACCESS_TOKEN = config('ACCESS_TOKEN')
        ACCESS_SECRET = config('ACCESS_SECRET')
        self.auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

        self.track_list = []
        for k, v in tweet_dict.items():
            for tl in v:
                self.track_list.append(tl)



    def connect_to_server_and_run(self, db_conn):
        while True:
            try:
                twitterStream = Stream(self.auth, listener(db_conn,self.track_list))
                twitterStream.filter(track=self.track_list)
            except Exception as e:
                print("Sleeping and restarting")
                print(e)
                time.sleep(5)


my_conn = DB_SQLite("twitter.db")
my_conn.create_table("tweet_sentiment", {"keyword": "TEXT", "unix_time": "INT", "tweet": "TEXT", "neg": "REAL", "neu": "REAL", "pos": "REAL", "compound": "REAL", "polarity": "REAL", "subjectivity": "REAL"})
# my_conn.insert_values("pandas_test2", {'name': 'AAPL', 'key': 1,'value': 231.6})
# my_conn.insert_values("pandas_test2", {'name': 'FB', 'key': 2,'value': 438.2})
# my_conn.insert_values("pandas_test2", {'name': 'MSFT', 'key': 3,'value': 542.9})
# my_conn.insert_values("pandas_test2", {'name': 'TSLA', 'key': 4,'value': 229.6})
# df = my_conn.sql_to_df("SELECT * from pandas_test2")
# print(df, df.info())

# my_conn = DB_SQLite("twitter.db")
# my_twitter_client = TwitterClient()
# my_twitter_client.connect_to_server_and_run(my_conn)