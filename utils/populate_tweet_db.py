import sys
sys.path.append(r"C:\Users\Richard\PycharmProjects\dash\YT_Dash_Tutorial")

from utils.db_and_twitter import DB_SQLite, TwitterClient

my_conn = DB_SQLite("twitter.db")
my_twitter_client = TwitterClient()
my_twitter_client.connect_to_server_and_run(my_conn)