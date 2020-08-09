# -*- coding: utf-8 -*-

from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objects as go

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
    + date.today().strftime("%Y-%m-%d")
    + """.
Cases and deaths data available for countries, US states, and US counties.
Tests data available for US states.

Sources: [The Covid Tracking Project](https://covidtracking.com/data)
and [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19).
"""
)

PLOTLY_COLORS = [
    "#1F77B4",
    "#FF7F0E",
    "#2CA02C",
    "#D62728",
    "#9467BD",
    "#8C564B",
    "#E377C2",
    "#7F7F7F",
    "#BCBD22",
    "#17BECF",
]
PLOTLY_CONFIG = {"displayModeBar": False}


def get_layout():
    return {
        "dragmode": False,
        "height": 500,
        "hovermode": "x",
        "margin": {"l": 75, "b": 75, "t": 75, "r": 75},
        "plot_bgcolor": "#fff",
        "showlegend": False,
        "title": {
            "font": {"size": 16},
            "x": 0.5,
            "xanchor": "center",
            "xref": "container",
            "y": 0.9,
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


def plot_trend(y, names, title, y_range=None):
    """Plot y trend by names"""
    n_names = len(names)
    if n_names == 0:
        colors = PLOTLY_COLORS[:1]
        names = INITIAL_COUNTRIES[:1]
    else:
        colors = PLOTLY_COLORS * int(np.ceil(n_names / 10))
    df = DF[DF["name"].isin(names)]
    fig = go.Figure()

    for i, name in enumerate(names):
        df1 = df[df["name"] == name]
        x1 = df1["date"].to_numpy()
        y1 = df1[y].to_numpy()
        line = {"color": colors[i]}
        fig.add_trace(go.Scatter(x=x1, y=y1, name=name, line=line))
        if ~np.isnan(y1[-1]) and n_names > 1:
            fig.add_annotation(
                x=x1[-1],
                y=y1[-1],
                text=name,
                font=line,
                showarrow=False,
                xanchor="left",
            )

    layout = get_layout()
    layout["title"]["text"] = title
    if y_range is not None:
        layout["yaxis"]["range"] = y_range
    fig.update_layout(layout)
    return fig


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
        dcc.Graph(id="plot-cases-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-cases-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-deaths-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-deaths-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-tests-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-tests-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-positivity-ac", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-positivity", config=PLOTLY_CONFIG),
    ],
)


@app.callback(
    Output("plot-cases-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_cases_ac_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "New cases per million, 7-day average"
    return plot_trend("cases_ac_pm", names, title)


@app.callback(
    Output("plot-cases-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_cases_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total cases per million"
    return plot_trend("cases_pm", names, title)


@app.callback(
    Output("plot-deaths-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_deaths_ac_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "New deaths per million, 7-day average"
    return plot_trend("deaths_ac_pm", names, title)


@app.callback(
    Output("plot-deaths-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_deaths_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total deaths per million"
    return plot_trend("deaths_pm", names, title)


@app.callback(
    Output("plot-tests-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_tests_ac_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "New tests per million, 7-day average"
    return plot_trend("tests_ac_pm", names, title)


@app.callback(
    Output("plot-tests-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_tests_pm(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total tests per million"
    return plot_trend("tests_pm", names, title)


@app.callback(
    Output("plot-positivity-ac", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_positivity_ac(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "New test positivity rate (%), 7-day average"
    y_range = [-1.5, 31.5]
    return plot_trend("positivity_ac", names, title, y_range)


@app.callback(
    Output("plot-positivity", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_positivity(countries, states, counties):
    names = combine_names(countries, states, counties)
    title = "Total test positivity rate (%)"
    y_range = [-1.5, 31.5]
    return plot_trend("positivity", names, title, y_range)


if __name__ == "__main__":
    app.run_server(debug=True)

