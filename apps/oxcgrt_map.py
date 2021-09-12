import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
import pickle
from pathlib import Path
import plotly.express as px
from utils.web_to_df import WebToDF

blob = WebToDF()

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

map_dd_list = [
    {'label': 'Oxford Stringency Index', 'value': 'stringency'},
    {'label': 'Total Cases per million population', 'value': 'Total cases per million'},
    {'label': 'Total Deaths per million population', 'value': 'Total deaths per million'},
    {'label': 'Daily Cases per million population', 'value': 'Smoothed daily cases per million'},
    {'label': 'Daily Deaths per million population', 'value': 'Smoothed daily deaths per million'},
    {'label': 'Total Cases', 'value': 'confirmed'},
    {'label': 'Total Deaths', 'value': 'deaths'},
    {'label': 'Daily Cases', 'value': 'daily_cases'},
    {'label': 'Daily Deaths', 'value': 'daily_deaths'},

]

projection_dd_list = [
    {'label': 'Equirectangular', 'value': 'equirectangular'},
    {'label': 'Mercator', 'value': 'mercator'},
    {'label': 'Azimuthal Equal Area', 'value': 'azimuthal equal area'},
    {'label': 'Conic Conformal', 'value': 'conic conformal'},
    {'label': 'Gnomonic', 'value': 'gnomonic'},
    {'label': 'Lavrayskiy7', 'value': 'kavrayskiy7'},
    {'label': 'Miller', 'value': 'miller'},
    {'label': 'Mollweide', 'value': 'mollweide'},
    {'label': 'Hammer', 'value': 'hammer'},
    {'label': 'Stereographic', 'value': 'stereographic'},
    {'label': 'Sinusoidal', 'value': 'sinusoidal'},
    {'label': 'Natural Earth', 'value': 'natural earth'},
    {'label': 'Transverse Mercator', 'value': 'transverse mercator'},
    {'label': 'Winkel Tripel', 'value': 'winkel tripel'},
    {'label': 'Orthographic', 'value': 'orthographic'},

]

colorscheme_dd_list = [
    {'label': 'Black body', 'value': 'blackbody'},
    {'label': 'Blue Red', 'value': 'bluered'},
    {'label': 'Dark Mint', 'value': 'darkmint'},
    {'label': 'Hot', 'value': 'hot'},
    {'label': 'Inferno', 'value': 'inferno'},
    {'label': 'Viridis', 'value': 'viridis'},
    {'label': 'Sunset', 'value': 'sunsetdark'},
    {'label': 'Plasma', 'value': 'plasma'},
    {'label': 'Teal Green', 'value': 'tealgrn'},
    {'label': 'Twilight', 'value': 'twilight'},
    {'label': 'Spectral', 'value': 'spectral'},
    {'label': 'Ice Fire', 'value': 'icefire'},
    {'label': 'Thermal', 'value': 'nthermal'},
    {'label': 'Portland', 'value': 'portland'},
    {'label': 'Army Rose', 'value': 'armyrose'},
    {'label': 'Yellow Green Blue', 'value': 'ylgnbu'},

]

layout = html.Div([
    dbc.Row([
        dbc.Col(html.P('Projection type:'), align='end'),
        dbc.Col(
            dcc.Dropdown(id='prj-dd',
                         options=projection_dd_list,
                         value='natural earth',
                         className='dash-bootstrap'),
        ),
        dbc.Col(html.P('Parameter to plot:'), align='end'),
        dbc.Col(
            dcc.Dropdown(id='wg-dd',
                         options=map_dd_list,
                         value='Total cases per million',
                         className='dash-bootstrap'), width=2
        ),
        dbc.Col(html.P('Animation speed:'), align='end'),
        dbc.Col(dcc.Slider(id='map-speed-slider', min=0, max=3, marks={0: "Crawl", 1: "Slow", 2: "Med", 3: "Fast"},
                           className='dash-bootstrap',
                            value=1)
        ),
        dbc.Col(html.P('Colour scheme:'), align='end'),
        dbc.Col(
            dcc.Dropdown(id='col-dd',
                         options=colorscheme_dd_list,
                         value='plasma',
                         className='dash-bootstrap'),
        )
    ]),
    dcc.Loading(dcc.Graph(id='graph-the'), type="cube"),
])

@app.callback(
    Output('graph-the', 'figure'),
    [Input('wg-dd', 'value'),
     Input('prj-dd', 'value'),
    Input('col-dd', 'value'),
    Input('map-speed-slider', 'value')]
)
def update_graph(column, prj, col_scheme, speed):
    frame_speed = 12*speed + 1
    transition_speed = 2*speed + 1
    fig = px.choropleth(blob.oxcgrt,
                        locations='Country',
                        animation_frame='date_value',
                        hover_name='Name',
                        projection=prj,
                        color=column,
                        height=1080,
                        color_continuous_scale=col_scheme)

    fig.update_layout(title=dict(font=dict(size=28), x=0.5, xanchor='center'),
                      margin=dict(l=60, r=60, t=50, b=50),
                      plot_bgcolor='#222', paper_bgcolor='#222', geo=dict(bgcolor='#222'), font = dict(color='#58F', size=16))
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = frame_speed
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = transition_speed

    return fig