import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from app import app
import pandas as pd
from utils.web_to_df import WebToDF
import plotly.express as px

blob = WebToDF()


layout = html.Div([
    dbc.Row([
        dbc.Col(html.P("Min. Country Population:"), width=1),
        dbc.Col(dcc.Slider(id='pop-slider', min=0, max=5, marks=blob.slider_dict['display'], className='dash-bootstrap', value=3), width=3),
        dbc.Col(html.P('Animation speed:'), width=1),
        dbc.Col(dcc.Slider(id='speed-slider', min=0, max=3, marks={0: "Crawl", 1: "Slow", 2: "Med", 3: "Fast"}, className='dash-bootstrap', value=2), width=2),
        dbc.Col(html.P('Animation smoothing:'), width=1),
        dbc.Col(dcc.Slider(id='smooth-slider', min=1, max=3, marks={1: "Coarse", 2: "Medium", 3: "Smooth"}, className='dash-bootstrap', value=2), width=1)
    ]),
    dbc.Row([
        dbc.Spinner(dcc.Graph(id='ox-bubble'), type='cube')
    ])
])

@app.callback(Output('ox-bubble', 'figure'),
              [Input('pop-slider', 'value'),
              Input('speed-slider', 'value'),
              Input('smooth-slider', 'value')])
def display_bubble_chart(population, speed, smooth):
    frame_speed = 5*speed + 1
    transition_speed = 5*speed/6 + 1

    pop_val = blob.slider_dict['calculate'][population]
    display_df = blob.oxcgrt[['Country', 'Name', 'stringency', 'Total deaths per million', 'date_value', 'Total cases per million', 'Continent', 'Population']]
    display_df = display_df[display_df['Population'] > pop_val]
    display_df = display_df.sort_values(['date_value', 'Country'], ascending=True)

    max_d = display_df['Total deaths per million'].max()
    display_df['stringency_rolling'] = display_df['stringency'].rolling(smooth*smooth).mean()
    display_df = display_df.fillna(0)


    fig = px.scatter(display_df, x='stringency_rolling', y='Total deaths per million', animation_frame='date_value',
                                hover_name='Name', range_x=[0,100], range_y=[0, max_d+1000], text='Country', size_max=180,
                                size='Total cases per million', color='Continent', height=950, width=2200,
                                labels=dict(stringency_rolling="Stringency Index", Continent="Select Continent"))
    fig.update_layout(plot_bgcolor='#222', paper_bgcolor='#222', font=dict(size=12, color='white'))
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = frame_speed
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = transition_speed
    return fig
