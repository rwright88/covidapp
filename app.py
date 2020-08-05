# -*- coding: utf-8 -*-

from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

DF = pd.read_csv("data/covid.csv")
COUNTRIES = [
    {"label": x, "value": x}
    for x in DF[DF["type"] == "country"]["name"].unique().tolist()
]
STATES = [
    {"label": x, "value": x}
    for x in DF[DF["type"] == "state"]["name"].unique().tolist()
]
COUNTIES = [
    {"label": x, "value": x}
    for x in DF[DF["type"] == "county"]["name"].unique().tolist()
]
INITIAL_COUNTRIES = ["united states"]

NOTES = dcc.Markdown(
    """
Last updated """
    + date.today().strftime("%B %#d")
    + """.
Cases and deaths data available for countries, US states, and US counties.
Tests data available for US states.

Sources: [The Covid Tracking Project](https://covidtracking.com/data)
and [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19).
"""
)

PLOTLY_CONFIG = {"displayModeBar": False}
PLOTLY_LAYOUT = {
    "dragmode": False,
    "hovermode": "x",
    "legend": {"title": {"text": ""}},
    "margin": {"l": 75, "b": 50, "t": 50, "r": 75},
    "plot_bgcolor": "#fff",
    "title": {
        "font": {"size": 16},
        "x": 0.5,
        "xanchor": "center",
        "xref": "paper",
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


def plot_trend(y, names, title, y_range=None):
    """Create trend plot of y by name"""
    if len(names) == 0:
        names = INITIAL_COUNTRIES[:1]
    df = DF[DF["name"].isin(names)]
    layout = PLOTLY_LAYOUT.copy()
    layout["title_text"] = title
    if len(names) == 1:
        layout["showlegend"] = False
    fig = px.line(df, x="date", y=y, color="name", height=500)
    fig.update_layout(layout)
    fig.update_traces(hovertemplate=None)
    if y_range is not None:
        fig.update_yaxes(range=y_range)
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
    style={"max-width": 1000, "margin-left": "auto", "margin-right": "auto"},
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
        dcc.Graph(id="deaths-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="deaths-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="tests-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="tests-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="positivity-ac", config=PLOTLY_CONFIG),
        dcc.Graph(id="positivity", config=PLOTLY_CONFIG),
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
    title = "New cases per million, 7-day average"
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
    Output("deaths-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_deaths_ac_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "New deaths per million, 7-day average"
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
    title = "New tests per million, 7-day average"
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
    Output("positivity-ac", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_positivity_ac(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "New test positivity rate (%), 7-day average"
    return plot_trend(y="positivity_ac", names=names, title=title, y_range=[-1.5, 31.5])


@app.callback(
    Output("positivity", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_positivity(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total test positivity rate (%)"
    return plot_trend(y="positivity", names=names, title=title, y_range=[-1.5, 31.5])


if __name__ == "__main__":
    app.run_server(debug=True)

