import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Sample Dash app to show numreic input, a text box and a dropdown"),
    dcc.Input(id="numeric", type="number", placeholder="1"),
    dcc.Input(id="text", type="text", placeholder="Sample Text"),
    dcc.Dropdown(
        id="dropdown", options=[{'label': "Goldman Sachs", 'value': "GS"},
                                {"label": "JPMorgan", "value": "JPM"}],
        placeholder="Goldman Sachs", value="GS"),
    html.Hr(),
    html.Div(id="number-out"),
    html.Div(id="text-out"),
    html.Div(id="dropdown-out"),
])
@app.callback(
    Output("number-out", "children"),
    Output("text-out", "children"),
    Output("dropdown-out", "children"),
    Input("numeric", "value"),
    Input("text", "value"),
    Input("dropdown", "value"),
)
def number_render(nval, tval, dval):
    return [nval, tval, dval]

if __name__ == "__main__":
    app.run_server(debug=True, port=8028)