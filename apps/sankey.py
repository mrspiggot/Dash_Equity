
from ast import literal_eval
import dash_html_components as html
import pandas as pd
import dash_core_components as dcc
from app import app
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


def get_spreadsheet_data(filename):
    df = pd.read_excel(filename)
    node = dict(zip(df['Key'], df['node']))
    link = dict(zip(df['Key'], df['link']))

    ret_node = {}
    ret_link = {}
    for k, v in node.items():
        if k in ['line', 'label', 'color']:
            ret_node[k] = literal_eval(v)

    for k, v in link.items():
        # if k in ['label', 'color', 'source', 'target', 'value']:
        if k in ['color', 'source', 'target', 'value']:
            ret_link[k] = literal_eval(v)
    return ret_node, ret_link

def get_budget_node_data():
        name = ['Salary', 'Investments', 'Tax', 'Retained Earnings', 'Food & Clothing', 'Household Bills', 'Travel', 'Entertainment', 'Savings', 'Pensions', 'Healthcare', 'Welfare', 'Education', 'Defense', 'Law & Order', 'Transportation', 'Foreign Aid']
        return name

def get_budget_link_data():
    source = [0, 0, 1, 1, 2,  2,  2,  2,  2,  2,  2,  2, 3, 3, 3, 3, 3]
    target = [2, 3, 2, 3, 9, 10, 11, 12, 13, 14, 15, 16, 4, 5, 6, 7, 8]
    value = [40, 60, 1.5, 8.5, 11.3, 9.7, 7.8, 5, 2.5, 2, 1.7, 1.4, 21, 18, 8, 13, 8.5]
    return source, target, value



layout = html.Div([
    dbc.Row([
        dbc.Col([html.P("Chart Type:")], width=1),
        dbc.Col([dcc.Dropdown(id='options',
                   options=[{'label': 'Household', 'value': 'household'},
                            {'label': 'Energy', 'value': 'energy'},
                            {'label': 'Portfolio', 'value': 'portfolio'}],
                   value='Energy',
                   className='dash-bootstrap')], width=2),
    ]),
    dcc.Graph(id="sankey-graph"),

])

@app.callback(
    Output("sankey-graph", "figure"),
    [Input("options", "value")])
def display_sankey(chart_type):

    if chart_type == 'energy':
        node, link = get_spreadsheet_data('assets/Sankey_Energy.xlsx')
        fig = go.Figure(go.Sankey(link=link, node=node))
        fig.update_layout(font=dict(size=18, color='white'), height=1050, plot_bgcolor='#222', paper_bgcolor='#222', )
    elif chart_type == 'portfolio':
        node, link = get_spreadsheet_data('assets/Sankey Portfolio.xlsx')
        fig = go.Figure(go.Sankey(link=link, node=node))
        fig.update_layout(font=dict(size=18, color='white'), height=1050, plot_bgcolor='#222', paper_bgcolor='#222', )
    else:
        name = get_budget_node_data()
        source, target, value = get_budget_link_data()

        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=5,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=name,
                customdata=name,
                hovertemplate='Node %{customdata} has total value %{value}<extra></extra>',
                # color_discrete_map=cmap,

            ),
            link=dict(
                source=source,
                # indices correspond to labels, eg A1, A2, A2, B1, ...
                target=target,
                value=value,
                # customdata=["q", "r", "s", "t", "u", "v"],
                # hovertemplate='Link from node %{source.customdata}<br />' +
                #               'to node%{target.customdata}<br />has value %{value}' +
                #               '<br />',
            ))])
        fig.update_layout(
            hovermode='x',
            title="Household Budget",
            font=dict(size=18, color='white'),
            height=1050,
            plot_bgcolor='#222',
            paper_bgcolor='#222',
            # color_discrete_map=cmap,
        )

    return fig


