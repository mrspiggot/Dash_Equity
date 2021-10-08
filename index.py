from app import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from utils.sp500_si import StockInfo
from apps import charts, heatmaps, benchmarks, composition, rebalancing, sankey, risk, twitter_charts, oxcgrt_bubble, oxcgrt_map, ticker

input_analysis_dropdown = dbc.DropdownMenu(
    children=[
        dbc.DropdownMenuItem("OxCGRT Bubble", href='/oxford_bubble'),
        dbc.DropdownMenuItem("OxCGRT Map", href='/oxford_map'),
        dbc.DropdownMenuItem("Twitter Sentiment", href='/twitter'),
    ],
    nav=True,
    in_navbar=True,
    label="Macro Analysis",
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(html.Img(src='assets/lucidate.png', height="90px")),
                        dbc.Col(dbc.NavbarBrand("Lucidate Sample Dash Finance App", className="ml-2", href='/home')),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="/",
            ),
            dbc.Nav(
                [dbc.NavItem(dbc.NavLink("Charts", href="/charts", disabled=False)),
                 dbc.NavItem(dbc.NavLink("Heatmaps", href="/heatmaps")),
                 dbc.NavItem(dbc.NavLink("Benchmarks", href="/benchmarks")),
                 dbc.NavItem(dbc.NavLink("Composition", href="/composition")),
                 dbc.NavItem(dbc.NavLink("Sankey", href="/sankey")),
                 dbc.NavItem(dbc.NavLink("Rebalancing", href="/rebalancing")),
                 dbc.NavItem(dbc.NavLink("Risk", href="/Value_At_Risk")),
                 dbc.NavItem(dbc.NavLink("Ticker", href="/ticker")),
                 input_analysis_dropdown,

                 ], className="ml-auto", navbar=True
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
)

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

def serve_layout():
    return html.Div([
    dcc.Location(id='page-url'),
    html.Div([
        navbar,
    ]),
    html.Div(id='page-content', children=[]),
],
style=CONTENT_STYLE)

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('page-url', 'pathname')], prevent_initial_call=True)
def display_page(pathname):
    if pathname == '/charts':
        return charts.layout
    if pathname == '/heatmaps':
        return heatmaps.layout
    if pathname == '/benchmarks':
        return benchmarks.layout
    if pathname == '/composition':
        return composition.layout
    if pathname == '/rebalancing':
        return rebalancing.layout
    if pathname == '/sankey':
        return sankey.layout
    if pathname == '/Value_At_Risk':
        return risk.layout
    if pathname == '/twitter':
        return twitter_charts.layout
    if pathname == '/oxford_bubble':
        return oxcgrt_bubble.layout
    if pathname == '/oxford_map':
        return oxcgrt_map.layout
    if pathname == '/ticker':
        return ticker.layout

if __name__ == '__main__':
    app.run_server(debug=True, port=8027)