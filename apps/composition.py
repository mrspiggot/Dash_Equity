import dash_html_components as html
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import pickle

with open('assets/ticker.pickle', 'rb') as handle:
    ticker_dict = pickle.load(handle)

def portfolio_sunburst():
    payload = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    df = payload[0]

    mkt_cap = pd.read_html("https://www.liberatedstocktrader.com/sp-500-companies/")
    second_table = mkt_cap[2]

    combined_df = df.merge(second_table, left_on=['Symbol'], right_on=1)
    combined_df.columns = combined_df.columns.astype(str)

    sp_df = combined_df[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', '3', '4']]
    sp_df.rename(columns={'GICS Sector': 'Sector', 'GICS Sub-Industry': 'Group', '3': 'Sub Industry', '4': 'Mkt Cap'},
                 inplace=True)
    sp_df["Mkt Cap"] = sp_df["Mkt Cap"].replace('[\$\,\.]', "", regex=True).astype(int)
    sp_df['Percent'] = sp_df['Mkt Cap'] / sp_df['Mkt Cap'].sum() * 100
    sp_df['Percent'] = sp_df['Percent'].round(2)

    cmap = {
        'Communication Services': 'orange',
        'Consumer Discretionary': 'yellow',
        'Consumer Staples': 'red',
        'Energy': 'black',
        'Financials': 'cyan',
        'Health Care': 'green',
        'Industrials': 'olive',
        'Information Technology': 'blue',
        'Materials': 'purple',
        'Real Estate': 'magenta',
        'Utilities': 'maroon'

    }

    fig = px.sunburst(sp_df, path=['Sector', 'Group', 'Security'], values='Percent', color='Sector',
                      color_discrete_map=cmap, height=800)
    fig.layout.plot_bgcolor='#222'
    fig.layout.paper_bgcolor='#222'


    port = pd.read_excel('assets/Historical Performance.xlsx')

    port['Percent'] = port['Yesterday Close'] * 100
    port['Percent'] = port['Percent'].round(2)



    fig2 = px.sunburst(port, path=['Industry', 'Sector', 'Name'], values='Percent', color='Industry',
                       color_discrete_map=cmap, height=800)

    fig2.layout.plot_bgcolor='#222'
    fig2.layout.paper_bgcolor='#222'

    return dbc.Row([
        dbc.Col(dcc.Graph(figure=fig), width=6),
        dbc.Col(dcc.Graph(figure=fig2), width=6)
    ])



layout = html.Div([
    html.H4('S&P (Left) & Portfolio (Right) sector composition weighted by market capitalization', style={'textAlign': 'center'}),
    portfolio_sunburst(),



])