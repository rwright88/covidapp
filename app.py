# -*- coding: utf-8 -*-

from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
PLOTLY_LAYOUT = {
    "dragmode": False,
    "height": 4000,
    "hovermode": "x",
    "margin": {"l": 50, "b": 50, "t": 50, "r": 50},
    "plot_bgcolor": "#fff",
    "showlegend": False,
}
PLOTLY_XAXES = {
    "fixedrange": True,
    "gridcolor": "#eee",
    "title": {"text": ""},
}
PLOTLY_YAXES = {
    "fixedrange": True,
    "gridcolor": "#eee",
    "title": {"text": ""},
    "zerolinecolor": "#eee",
    "zerolinewidth": 2,
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
        dcc.Graph(id="plot-everything", config=PLOTLY_CONFIG),
    ],
)


@app.callback(
    Output("plot-everything", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
    ],
)
def plot_everything(countries, states, counties):
    data = {
        "cases_ac_pm": "New cases per million, 7-day average",
        "cases_pm": "Total cases per million",
        "deaths_ac_pm": "New deaths per million, 7-day average",
        "deaths_pm": "Total deaths per million",
        "tests_ac_pm": "New tests per million, 7-day average",
        "tests_pm": "Total tests per million",
        "positivity_ac": "New test positivity rate (%), 7-day average",
        "positivity": "Total test positivity rate (%)",
    }
    names = combine_names(countries, states, counties)
    n_names = len(names)
    if n_names == 0:
        names = INITIAL_COUNTRIES[:1]
    df = DF[DF["name"].isin(names)]
    colors = PLOTLY_COLORS.copy() * int(np.ceil(n_names / 10))
    cols = list(data.keys())
    titles = list(data.values())
    n_plots = len(cols)
    fig = make_subplots(
        rows=n_plots, cols=1, subplot_titles=titles, vertical_spacing=0.03
    )

    for i, name in enumerate(names):
        df1 = df[df["name"] == name]
        x = df1["date"].to_numpy()
        line = {"color": colors[i]}
        for i in range(n_plots):
            y = df1[cols[i]].to_numpy()
            fig.add_trace(go.Scatter(x=x, y=y, name=name, line=line), row=i + 1, col=1)
            if not np.isnan(y[-1]):
                fig.add_annotation(
                    x=x[-1],
                    y=y[-1],
                    text=name,
                    font=line,
                    showarrow=False,
                    xanchor="left",
                    row=i + 1,
                    col=1,
                )

    fig.update_layout(PLOTLY_LAYOUT)
    fig.update_xaxes(PLOTLY_XAXES)
    fig.update_yaxes(PLOTLY_YAXES)
    fig.update_yaxes(range=[-1.5, 31.5], row=7, col=1)
    fig.update_yaxes(range=[-1.5, 31.5], row=8, col=1)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

