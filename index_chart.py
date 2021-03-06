from app import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from apps import charts #, heatmaps, benchmarks, composition, rebalancing, sankey, risk, twitter_charts, oxcgrt_bubble, oxcgrt_map

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
                 input_analysis_dropdown,

                 ], className="ml-auto", navbar=True
            ),
        ]
    ),
    color="dark", dark=True, className="mb-5",
)

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

def serve_layout():
    return html.Div([
    dcc.Location(id='page-url'), # This 'Location' component will change when an Navbar item is selected. When this
                                 # Location component changes the callback is fired. It is the 'Input' callback (c/b)
    html.Div([
        navbar,                  # This Navbar will appear on every page
    ]),
    html.Div(id='page-content', children=[]),  # This component is a generic container that will serve all of
    ], style=CONTENT_STYLE                     # the content generated by the Navbar selections. It is the 'Output' c/b
)

app.layout = serve_layout

@app.callback(Output('page-content', 'children'),
              [Input('page-url', 'pathname')], prevent_initial_call=True)
def display_page(pathname):

    if pathname == '/charts':
        return charts.layout
    else:
        return (html.H1("Navbar item selected is: " + str(pathname)))


if __name__ == '__main__':
    app.run_server(debug=True, port=8032)