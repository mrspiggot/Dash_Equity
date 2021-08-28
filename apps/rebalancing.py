import json
import urllib


import dash_html_components as html
import plotly.express as px
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd
import pickle
from app import app
from dash.dependencies import Input, Output
import plotly.graph_objects as go

url = 'https://raw.githubusercontent.com/plotly/plotly.js/master/test/image/mocks/sankey_energy.json'
response = urllib.request.urlopen(url)
data = json.loads(response.read())


layout = html.Div([
    dcc.Dropdown(id='opacity'),
    dcc.Graph(id="graph"),
    html.P("Opacity"),

])

@app.callback(
    Output("graph", "figure"),
    [Input("opacity", "value")])
def display_sankey(opacity):
    opacity = str(opacity)

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

    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 5,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = ["Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials", "Health Care", "Industrials", "Information Technology", "Materials", "Real Estate", "Utilities",
                        "Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials", "Health Care", "Industrials", "Information Technology", "Materials", "Real Estate", "Utilities",],
          customdata = ["Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials", "Health Care", "Industrials", "Information Technology", "Materials", "Real Estate", "Utilities",
                        "Communication Services", "Consumer Discretionary", "Consumer Staples", "Energy", "Financials", "Health Care", "Industrials", "Information Technology", "Materials", "Real Estate", "Utilities",],
          hovertemplate='Node %{customdata} has total value %{value}<extra></extra>',
          # color_discrete_map=cmap,

        ),
        link = dict(
          source = [0, 0,  1,   2,   3,   4,  3,   3,   3, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], # indices correspond to labels, eg A1, A2, A2, B1, ...
          target = [11, 18,  18,   18,   18,   18,  16,   19,   20, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
          value = [8, 0.3, 9.7, 7.5, 3.9, 2.5, 0.8, 0.1, 0.1, 24.5, 8.9, 1.3, 5.8, 16.9, 5.3, 24.7, 2.9, 0.8, 0.9],
          customdata = ["q","r","s","t","u","v"],
          hovertemplate='Link from node %{source.customdata}<br />'+
            'to node%{target.customdata}<br />has value %{value}'+
            '<br />',
      ))])
    fig.update_layout(
        hovermode='x',
        title="Portfolio Rebalancing",
        font=dict(size=10, color='white'),
        height=880,
        plot_bgcolor='#222',
        paper_bgcolor='#222',
        # color_discrete_map=cmap,
    )

    # # override gray link colors with 'source' colors
    # node = data['data'][0]['node']
    # link = data['data'][0]['link']
    #
    # # Change opacity
    # node['color'] = [
    #     'rgba(255,0,255,{})'.format(opacity)
    #     if c == "magenta" else c.replace('0.8', opacity)
    #     for c in node['color']]
    #
    # link['color'] = [
    #     node['color'][src] for src in link['source']]
    #
    # fig = go.Figure(go.Sankey(link=link, node=node))
    fig.update_layout(font_size=10)
    fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
    return fig

