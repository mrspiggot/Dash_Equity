import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from app import app
import pandas as pd
import sqlite3
import plotly
import plotly.graph_objs as go
tweet_dict={'entertainment': ['Drake', 'ABBA', 'Kanye', 'Kardashian'],
            'crypto': ['BTC', 'ADA', 'ETH', 'XRP', 'DOGE', 'LTC'],
            'politics': ['Trump', 'Biden', 'Covid', 'Afghanistan', 'Brexit']}

smooth_dict={0: 10, 1: 40, 2: 200, 3: 400}
POS_NEG_NEUT = 0.1
app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

def generate_table(df, max_rows=10):
    return dbc.Table(hover=True, size='sm',
                      children=[
                          html.Thead(
                              html.Tr(
                                  children=[
                                      html.Th(col) for col in df.columns.values],
                                  style={'color': app_colors['text']}
                              )
                          ),
                          html.Tbody(
                              [

                                  html.Tr(
                                      children=[
                                          html.Td(data) for data in d
                                      ], style={'color': app_colors['text'],
                                                'background-color': quick_color(d[2])}
                                  )
                                  for d in df.values.tolist()])
                      ]
                      )

def quick_color(s):
    # except return bg as app_colors['background']
    if s >= POS_NEG_NEUT:
        # positive
        return "#002C0D"
    elif s <= -POS_NEG_NEUT:
        # negative:
        return "#270000"

    else:
        return app_colors['background']


subject_options = []
for key in tweet_dict.keys():
    d = {'value': key, 'label': key.capitalize()}
    subject_options.append(d)

dropdown_options = {}
for key, value in tweet_dict.items():
    options = []
    for v in value:
        d = {'value': v, 'label': v}
        options.append(d)
    dropdown_options[key] = options

layout = html.Div([
    dbc.Row([
        dbc.Col(html.P("Subject: "), width={'size': 1, 'offset': 1, 'order': 'first'}),
        dbc.Col(dcc.Dropdown(id='subject-dd', options=subject_options, placeholder="Politics",
                             className='dash-bootstrap'),
                width={'size': 1}),
        dbc.Col(html.P("Twitter search term:"), width={'size': 1}),
        dbc.Col(dcc.Dropdown(id="tw-item-dd", className='dash-bootstrap', placeholder='Trump', value="Trump"),
                width={'size': 1}),
        dbc.Col(html.P("Sentiment sensitivity:"), width={'size': 1}),
        dbc.Col(dcc.Slider(id='sensitivity-sl', min=1, max=3, marks={1: "Low", 2: "Med", 3: "High"},
                           className='dash-bootstrap', value=2), width={'size': 2}),
        dbc.Col(html.P("Smoothing:"), width={'size': 1}),
        dbc.Col(dcc.Slider(id='smoothing-sl', min=0, max=3, marks={0: "Smooth", 1: "Slow", 2: "Med", 3: "Reactive"},
                           className='dash-bootstrap', value=1), width={'size': 2})
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='live-graph', animate=True),
            width=6,
        ),
        dbc.Col(dcc.Graph(id='pie-chart', animate=False),
                width=6,
        ),

    ]),
    dbc.Row([
        dbc.Col(html.Div(id="recent-tweets-table"),
            width=6, lg={'size': 6,  "offset": 0, 'order': 'first'}
            ),
        dbc.Col(dcc.Graph(id='live-radar', animate=False),
                width=6,
        ),
    ]),

    dcc.Interval(
        id='graph-update',
        interval=1*1000,
        n_intervals=0
    ),

])
@app.callback([Output('tw-item-dd', 'options'),
               Output('tw-item-dd', 'value')],
               Input('subject-dd', 'value'))
def populate_dropdown(choice):
    if choice == None:
        choice = 'politics'

    dd_str = dropdown_options[choice][0]['value']
    return [dropdown_options[choice], dd_str]

@app.callback(Output('live-radar', 'figure'),
              [Input('graph-update', 'n_intervals'),
               Input('tw-item-dd', 'value'),
               Input('sensitivity-sl', 'value'),
               Input('smoothing-sl', 'value'),
               Input('subject-dd', 'value')])
def update_sentiment_radar_plot(n_int, twitter_item, sensitivity, smoothing, subject):
    if subject == None:
        subject = 'politics'

    fig = go.Figure()
    for keyword in tweet_dict[subject]:
        query_string = "SELECT * from tweet_sentiment where keyword = '" + str(keyword) + "' order by unix_time DESC LIMIT 2000"
        conn = sqlite3.connect("utils/twitter.db")
        df = pd.read_sql(query_string, conn)
        if smooth_dict[smoothing] > int(len(df)):
            window = 1
            max_iter = 0
        else:
            window = int(len(df) / smooth_dict[smoothing])
            max_iter= min(19, len(df))

        df.sort_values('unix_time', ascending=True, inplace=True)
        df[['smoothed_neu', 'smoothed_pos', 'smoothed_neg', 'smoothed_compound', 'smoothed_polarity', 'smoothed_subjectivity']] = df[
            ['neu', 'pos', 'neg', 'compound', 'polarity', 'subjectivity']].rolling(window).mean()
        df['date'] = pd.to_datetime(df['unix_time'], unit='ms')
        df.set_index('date', inplace=True)
        df.dropna(inplace=True)

        neu = 0
        neg = 0
        pos = 0
        com = 0
        pol = 0
        sub = 0

        for i in range(0, max_iter):
            neu += (df['smoothed_neu'].iloc[i]) / sensitivity
            pos += (df['smoothed_pos'].iloc[i]) * sensitivity
            neg += (df['smoothed_neg'].iloc[i]) * sensitivity
            com += (df['smoothed_compound'].iloc[i])
            pol += (df['smoothed_polarity'].iloc[i])
            sub += (df['smoothed_subjectivity'].iloc[i])

        labels = ['Neutral', 'Positive', 'Negative', 'Compound', 'Polarity', 'Subjectivity']
        values = [neu, pos, neg, com, pol, sub]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            opacity=0.5,
            fill='toself',
            name=keyword
        ))
    title_string = subject.capitalize() + " Radar Plot"
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-5, 10]
            )),
        showlegend=True,
        plot_bgcolor = '#222',
        paper_bgcolor = '#222',
        polar_bgcolor = '#222',
        font = dict(color='#58F', size=16),
        title=title_string,
        height=650,
    )
    return fig

@app.callback([Output('live-graph', 'figure'),
               Output('recent-tweets-table', 'children'),
               Output('pie-chart', 'figure')],
              [Input('graph-update', 'n_intervals'),
               Input('tw-item-dd', 'value'),
               Input('sensitivity-sl', 'value'),
               Input('smoothing-sl', 'value')])
def update_sentiment_area_chart(n_int, twitter_item, sensitivity, smoothing):
    query_string = "SELECT * from tweet_sentiment where keyword = '" + str(twitter_item) + "' order by unix_time DESC LIMIT 2500"
    conn = sqlite3.connect("utils/twitter.db")
    df = pd.read_sql(query_string, conn)
    if smooth_dict[smoothing] > int(len(df)):
        window = 1
        max_iter = 0
    else:
        window = int(len(df) / smooth_dict[smoothing])
        max_iter = min(19, len(df))

    df.sort_values('unix_time', ascending=True, inplace=True)
    df[['smoothed_neu', 'smoothed_pos', 'smoothed_neg', 'smoothed_compound']] = df[
        ['neu', 'pos', 'neg', 'compound']].rolling(window).mean()
    df['date'] = pd.to_datetime(df['unix_time'], unit='ms')
    df.set_index('date', inplace=True)
    df.dropna(inplace=True)

    X = df.index[-20:]
    Y = df.smoothed_neu.values[-20:]

    Y = Y / sensitivity
    Y2 = df.smoothed_pos.values[-20:]

    Y2 = Y2 * sensitivity
    Y3 = df.smoothed_neg.values[-20:]
    Y3 = Y3 * -sensitivity

    data = plotly.graph_objs.Scatter(
        x=X,
        y=Y,
        name='Neutral',
        mode='lines',
        stackgroup="three",
        line_shape='spline'
    )

    data2 = plotly.graph_objs.Scatter(
        x=X,
        y=Y3,
        name='Negative',
        mode='lines',
        opacity=0.3,
        stackgroup="two",
        line_shape='spline',
        fillcolor="#A00"

    )
    data3 = plotly.graph_objs.Scatter(
        x=X,
        y=Y2,
        name='Positive',
        mode='lines',
        opacity=0.2,
        stackgroup="one",
        line_shape='spline',


    )
    neu = 0
    neg = 0
    pos = 0
    for i in range(0, max_iter):
        neu += (df['smoothed_neu'].iloc[i]) / sensitivity
        pos += (df['smoothed_pos'].iloc[i]) * sensitivity
        neg += (df['smoothed_neg'].iloc[i]) * sensitivity

    labels = ['Neutral', 'Positive', 'Negative']
    values = [neu, pos, neg]
    colors = ['royalblue', 'green', 'red']
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.7)],
                    layout=go.Layout(plot_bgcolor='#222',
                                paper_bgcolor='#222',
                                height=480,
                                font=dict(color='#58C', size=18)
                                )
                    )
    title="Keyword = '<b><i>" + str(twitter_item) + "</i></b>'<br>Long-Term Moving<br>Average Sentiment"
    fig.update_traces(title=title, hoverinfo='label+percent', textinfo='percent', textfont_size=20,
                      marker=dict(colors=colors, line=dict(color='#888888', width=0.5)))

    title_string = "Short-Term Twitter Sentiment trace"
    styling = go.Layout(title=title_string, xaxis=dict(range=[min(X), max(X)], title="Time (GMT)"),
                                yaxis_title="Sentiment strength",
                                plot_bgcolor='#222',
                                paper_bgcolor='#222',
                                font=dict(color='#58C'),
                                )
    df['display_date'] = pd.to_datetime(df['unix_time'],  unit='ms').apply(lambda x: x.to_datetime64())
    # df['display_date'] = pd.to_datetime(df['display_date']).dt.floor('s')
    df['Time'] = pd.to_datetime(df['display_date']).dt.floor('s')
    df = df[['Time','tweet','compound']]
    df = df.sort_values(['Time'], ascending=False)
    df.rename(columns={'compound': 'Sentiment', 'Time': 'Date and Timestamp (UTC)', 'tweet': 'Tweet'}, inplace=True)

    df = df.round(2)
    df = df.head(15)

    return [{'data': [data, data2, data3],'layout': styling},
            generate_table(df, max_rows=10),
            fig]