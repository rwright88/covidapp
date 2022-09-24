# -*- coding: utf-8 -*-

from datetime import date

from dash.dependencies import Input, Output
import dash
from dash import dcc
from dash import html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import s3fs


def read_data(path):
    cols = {
        "type": "category",
        "name": "category",
        "date": np.datetime64,
        "cases_ac_pm": float,
        "cases_pm": float,
        "deaths_ac_pm": float,
        "deaths_pm": float,
        "hosp_a_pm": float,
        "tests_ac_pm": float,
        "tests_pm": float,
        "vaccinations_ac_pm": float,
        "vaccinations_pm": float,
    }
    dtypes = {k: v for k, v in cols.items() if k != "date"}
    df = pd.read_csv(path, usecols=cols.keys(), dtype=dtypes, parse_dates=["date"])
    return df


DF = read_data("s3://rwright-covid/covid.csv")
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

View code and data sources [here](https://github.com/rwright88/covid).
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


def get_layout_plot():
    return {
        "dragmode": False,
        "height": 500,
        "hovermode": "x",
        "margin": {"l": 75, "r": 75, "t": 75, "b": 75},
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
        "xaxis": {
            "fixedrange": True,
            "gridcolor": "#eee",
            "title": {"text": ""},
            "type": "date",
        },
        "yaxis": {
            "fixedrange": True,
            "gridcolor": "#eee",
            "title": {"text": ""},
            "zerolinecolor": "#eee",
            "zerolinewidth": 2,
        },
    }


def get_layout_map():
    return {
        "dragmode": False,
        "geo": {"scope": "usa", "showlakes": False},
        "height": 600,
        "margin": {"l": 75, "r": 75, "t": 75, "b": 75},
        "plot_bgcolor": "#fff",
        "title": {
            "font": {"size": 16},
            "x": 0.5,
            "xanchor": "center",
            "xref": "container",
            "y": 0.9,
            "yanchor": "bottom",
            "yref": "container",
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


def plot_trend(y, names, title, x_range="all"):
    """Plot trend"""
    n_names = len(names)
    if n_names == 0:
        colors = PLOTLY_COLORS[:1]
        names = INITIAL_COUNTRIES[:1]
    else:
        colors = PLOTLY_COLORS * int(np.ceil(n_names / 10))
    df = DF[DF["name"].isin(names)]

    if y in ["vaccinations_ac_pm", "vaccinations_pm"]:
        df = df[df["date"] >= "2020-12-15"]

    if x_range == "last6":
        df = df[df["date"] >= (df["date"].max() - pd.Timedelta(180, unit="D"))]
    elif x_range == "last3":
        df = df[df["date"] >= (df["date"].max() - pd.Timedelta(90, unit="D"))]

    y_max = df[y].max() * 1.05
    y_min = 0 - y_max / 1.05 * 0.05

    fig = go.Figure()

    for i, name in enumerate(names):
        df1 = df[df["name"] == name]
        x1 = df1["date"]
        y1 = df1[y].to_numpy()
        line = {"color": colors[i]}
        fig.add_trace(go.Scatter(x=x1, y=y1, name=name, line=line, connectgaps=True))

        if np.sum(~np.isnan(y1)) > 0 and n_names > 1:
            ind = np.max(np.argwhere(~np.isnan(y1)))
            fig.add_annotation(
                x=x1.iloc[ind],
                y=y1[ind],
                text=name,
                font=line,
                showarrow=False,
                xanchor="left",
            )

    layout = get_layout_plot()
    layout["title"]["text"] = title
    layout["yaxis"]["range"] = [y_min, y_max]
    fig.update_layout(layout)
    return fig


def map_current(val, title, z_range=None):
    """Map current values"""
    state = DF.loc[DF["type"] == "state", ["name", "date", val]]
    state = state[state[val].notna()]
    current = state[state["date"] == state["date"].max()]

    if z_range is None:
        z_range = [0, current[val].quantile(0.95)]

    data = {
        "type": "choropleth",
        "locations": current["name"].str.upper(),
        "locationmode": "USA-states",
        "z": current[val],
        "zmin": z_range[0],
        "zmax": z_range[1],
        "colorscale": "Blues",
        "colorbar": {"len": 0.5},
    }
    layout = get_layout_map()
    layout["title"]["text"] = title
    fig = go.Figure(data)
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
        dcc.RadioItems(
            id="id_dates",
            options=[
                {"label": "All data", "value": "all"},
                {"label": "Last 6 months", "value": "last6"},
                {"label": "Last 3 months", "value": "last3"},
            ],
            value="all",
            labelStyle={"display": "inline-block"},
            style={"margin-top": "5px"},
        ),

        html.H2("Cases"),
        dcc.Graph(id="plot-cases-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-cases-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-cases-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-cases-pm", config=PLOTLY_CONFIG),

        html.H2("Deaths"),
        dcc.Graph(id="plot-deaths-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-deaths-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-deaths-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-deaths-pm", config=PLOTLY_CONFIG),

        html.H2("Tests"),
        dcc.Graph(id="plot-tests-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-tests-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-tests-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-tests-pm", config=PLOTLY_CONFIG),

        html.H2("Hospitalizations"),
        dcc.Graph(id="plot-hosp-a-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-hosp-a-pm", config=PLOTLY_CONFIG),

        html.H2("Vaccinations"),
        dcc.Graph(id="plot-vaccinations-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="plot-vaccinations-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-vaccinations-ac-pm", config=PLOTLY_CONFIG),
        dcc.Graph(id="map-vaccinations-pm", config=PLOTLY_CONFIG),
    ],
)


@app.callback(
    Output("plot-cases-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_cases_ac_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "New cases per million, 7-day average"
    return plot_trend("cases_ac_pm", names=names, title=title, x_range=dates)


@app.callback(
    Output("plot-cases-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_cases_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "Total cases per million"
    return plot_trend("cases_pm", names=names, title=title, x_range=dates)


@app.callback(Output("map-cases-ac-pm", "figure"), [Input("id_dates", "value")])
def map_cases_ac_pm(dates):
    title = "New cases per million, 7-day average"
    z_range = None
    return map_current("cases_ac_pm", title=title, z_range=z_range)


@app.callback(Output("map-cases-pm", "figure"), [Input("id_dates", "value")])
def map_cases_pm(dates):
    title = "Total cases per million"
    z_range = None
    return map_current("cases_pm", title=title, z_range=z_range)


@app.callback(
    Output("plot-deaths-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_deaths_ac_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "New deaths per million, 7-day average"
    return plot_trend("deaths_ac_pm", names=names, title=title, x_range=dates)


@app.callback(
    Output("plot-deaths-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_deaths_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "Total deaths per million"
    return plot_trend("deaths_pm", names=names, title=title, x_range=dates)


@app.callback(Output("map-deaths-ac-pm", "figure"), [Input("id_dates", "value")])
def map_deaths_ac_pm(dates):
    title = "New deaths per million, 7-day average"
    z_range = None
    return map_current("deaths_ac_pm", title=title, z_range=z_range)


@app.callback(Output("map-deaths-pm", "figure"), [Input("id_dates", "value")])
def map_deaths_pm(dates):
    title = "Total deaths per million"
    z_range = None
    return map_current("deaths_pm", title=title, z_range=z_range)


@app.callback(
    Output("plot-tests-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_tests_ac_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "New tests per million, 7-day average"
    return plot_trend("tests_ac_pm", names=names, title=title, x_range=dates)


@app.callback(
    Output("plot-tests-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_tests_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "Total tests per million"
    return plot_trend("tests_pm", names=names, title=title, x_range=dates)


@app.callback(Output("map-tests-ac-pm", "figure"), [Input("id_dates", "value")])
def map_tests_ac_pm(dates):
    title = "New tests per million, 7-day average"
    z_range = None
    return map_current("tests_ac_pm", title=title, z_range=z_range)


@app.callback(Output("map-tests-pm", "figure"), [Input("id_dates", "value")])
def map_tests_pm(dates):
    title = "Total tests per million"
    z_range = None
    return map_current("tests_pm", title=title, z_range=z_range)


@app.callback(
    Output("plot-hosp-a-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_hosp_a_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "Currently hospitalized per million, 7-day average"
    return plot_trend("hosp_a_pm", names=names, title=title, x_range=dates)


@app.callback(Output("map-hosp-a-pm", "figure"), [Input("id_dates", "value")])
def map_hosp_a_pm(dates):
    title = "Currently hospitalized per million, 7-day average"
    z_range = None
    return map_current("hosp_a_pm", title=title, z_range=z_range)


@app.callback(
    Output("plot-vaccinations-ac-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_vaccinations_ac_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "New vaccinations per million, 7-day average"
    return plot_trend("vaccinations_ac_pm", names=names, title=title, x_range=dates)


@app.callback(
    Output("plot-vaccinations-pm", "figure"),
    [
        Input("id_countries", "value"),
        Input("id_states", "value"),
        Input("id_counties", "value"),
        Input("id_dates", "value"),
    ],
)
def plot_vaccinations_pm(countries, states, counties, dates):
    names = combine_names(countries, states, counties)
    title = "Total vaccinations per million"
    return plot_trend("vaccinations_pm", names=names, title=title, x_range=dates)


@app.callback(Output("map-vaccinations-ac-pm", "figure"), [Input("id_dates", "value")])
def map_vaccinations_ac_pm(dates):
    title = "New vaccinations per million, 7-day average"
    z_range = None
    return map_current("vaccinations_ac_pm", title=title, z_range=z_range)


@app.callback(Output("map-vaccinations-pm", "figure"), [Input("id_dates", "value")])
def map_vaccinations_pm(dates):
    title = "Total vaccinations per million"
    z_range = None
    return map_current("vaccinations_pm", title=title, z_range=z_range)


if __name__ == "__main__":
    app.run_server(debug=True)
