# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

DF = pd.read_csv("data/covid.csv")
COUNTRIES = DF[DF["type"] == "country"]["name"].unique().tolist()
STATES = DF[DF["type"] == "state"]["name"].unique().tolist()
COUNTIES = DF[DF["type"] == "county"]["name"].unique().tolist()
COUNTRIES = [{"label": x, "value": x} for x in COUNTRIES]
STATES = [{"label": x, "value": x} for x in STATES]
COUNTIES = [{"label": x, "value": x} for x in COUNTIES]
INITIAL_COUNTRIES = ["united states"]
INITIAL_STATES = ["pa"]

NOTES = dcc.Markdown(
    """
Last updated July 17.
Cases and deaths data available for countries, US states, and US counties.
Tests data available for US states.

Sources: [The Covid Tracking Project](https://covidtracking.com/data)
and [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19).
"""
)

PLOTLY_CONFIG = {"displayModeBar": False}
PLOTLY_LAYOUT = {
    "hovermode": "x",
    "legend": {"title": {"text": ""}},
    "margin": {"l": 75, "b": 50, "t": 50, "r": 75},
    "plot_bgcolor": "#fff",
    "title": {
        "font": {"size": 16},
        "x": 0.5,
        "xanchor": "center",
        "xref": "container",
        "y": 0.92,
        "yanchor": "bottom",
        "yref": "container",
    },
    "xaxis": {"fixedrange": True, "gridcolor": "#eee", "title": {"text": ""}},
    "yaxis": {
        "fixedrange": True,
        "gridcolor": "#eee",
        "title": {"text": ""},
        "zerolinecolor": "#eee",
        "zerolinewidth": 2,
    },
}


def plot_trend(y, names, title):
    """Create trend plot of y by name"""
    if len(names) == 0:
        names = INITIAL_COUNTRIES[:1]
    df = DF[DF["name"].isin(names)]
    layout = PLOTLY_LAYOUT.copy()
    layout["title_text"] = title
    fig = px.line(df, x="date", y=y, color="name", height=500)
    fig.update_layout(layout)
    fig.update_traces(hovertemplate=None)
    return fig


def combine_names(countries, states, counties):
    """Combine country, state, and county selections into one list"""
    if countries is None:
        countries = []
    if states is None:
        states = []
    if counties is None:
        counties = []
    names = countries + states + counties
    return names


app = dash.Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

app.layout = html.Div(
    style={"max-width": 1050, "margin-left": "auto", "margin-right": "auto"},
    children=[
        html.H1("COVID-19 data"),
        html.P(NOTES),
        html.Label("Choose any combination of countries, US states, and US counties:"),
        dcc.Dropdown(
            id="id_countries",
            options=COUNTRIES,
            value=INITIAL_COUNTRIES,
            multi=True,
            placeholder="Select countries",
            style={"margin-top": "5px"},
        ),
        dcc.Dropdown(
            id="id_states",
            options=STATES,
            value=INITIAL_STATES,
            multi=True,
            placeholder="Select US states",
            style={"margin-top": "5px"},
        ),
        dcc.Dropdown(
            id="id_counties",
            options=COUNTIES,
            multi=True,
            placeholder="Select US counties",
            style={"margin-top": "5px"},
        ),
        dcc.Graph(id="cases-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="cases-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="tests-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="tests-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="deaths-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="deaths-pm", config=PLOTLY_CONFIG),
    ],
)


@app.callback(
    Output("cases-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_cases_ac_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Average daily new cases in the last 7 days per million"
    return plot_trend(y="cases_ac_pm", names=names, title=title)


@app.callback(
    Output("cases-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_cases_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total cases per million"
    return plot_trend(y="cases_pm", names=names, title=title)


@app.callback(
    Output("tests-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_tests_ac_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Average daily new tests in the last 7 days per million"
    return plot_trend(y="tests_ac_pm", names=names, title=title)


@app.callback(
    Output("tests-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_tests_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total tests per million"
    return plot_trend(y="tests_pm", names=names, title=title)


@app.callback(
    Output("deaths-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_deaths_ac_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Average daily new deaths in the last 7 days per million"
    return plot_trend(y="deaths_ac_pm", names=names, title=title)


@app.callback(
    Output("deaths-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_deaths_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total deaths per million"
    return plot_trend(y="deaths_pm", names=names, title=title)


if __name__ == "__main__":
    app.run_server(debug=True)

