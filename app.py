# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

app = dash.Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

DF = pd.read_csv("data/us.csv")
NAMES = [{"label": x, "value": x} for x in DF["name"].unique().tolist()]
NAMES_INITIAL = ["us", "pa"]
CONFIG = {"displayModeBar": False}

NOTES = dcc.Markdown(
    """
Last updated July 9. Cases and deaths data available for states and counties.
Tests data available for states.

Sources: [The Covid Tracking Project](https://covidtracking.com/data)
and [Johns Hopkins](https://github.com/CSSEGISandData/COVID-19).
"""
)
LABEL = dcc.Markdown(
    """
Choose any number of states (two-letter code) or counties (two-letter code, county name):
"""
)

app.layout = html.Div(
    style={"max-width": 1000, "margin-left": "auto", "margin-right": "auto"},
    children=[
        html.H1(children="US COVID-19 data"),
        html.P(children=NOTES),
        html.Label(LABEL),
        dcc.Dropdown(id="ids", options=NAMES, value=NAMES_INITIAL, multi=True),
        dcc.Graph(id="cases-ac-pm", config=CONFIG),
        dcc.Graph(id="cases-pm", config=CONFIG),
        dcc.Graph(id="tests-ac-pm", config=CONFIG),
        dcc.Graph(id="tests-pm", config=CONFIG),
        dcc.Graph(id="deaths-ac-pm", config=CONFIG),
        dcc.Graph(id="deaths-pm", config=CONFIG),
    ],
)

PLOTLY_LAYOUT = {
    "hovermode": "x",
    "legend_title_text": "",
    "margin": {"l": 50, "b": 50, "t": 50, "r": 50},
    "plot_bgcolor": "#fff",
    "title_font_size": 16,
    "title_x": 0.5,
    "title_xanchor": "center",
    "title_xref": "container",
    "title_y": 0.92,
    "title_yanchor": "bottom",
    "title_yref": "container",
    "xaxis_fixedrange": True,
    "xaxis_gridcolor": "#eee",
    "xaxis_title_text": "",
    "yaxis_fixedrange": True,
    "yaxis_gridcolor": "#eee",
    "yaxis_title_text": "",
    "yaxis_zerolinecolor": "#eee",
    "yaxis_zerolinewidth": 2,
}


def plot_trend(y, names=None, title=None):
    """Create trend plot of y by name"""
    if isinstance(names, str):
        names = [names]
    elif len(names) == 0:
        names = NAMES_INITIAL[:1]
    df = DF[DF["name"].isin(names)]
    fig = px.line(df, x="date", y=y, color="name", height=500)
    layout = PLOTLY_LAYOUT.copy()
    layout["title_text"] = title
    fig.update_traces(hovertemplate=None)
    fig.update_layout(layout)
    return fig


@app.callback(Output("cases-ac-pm", "figure"), [Input("ids", "value")])
def plot_cases_ac_pm(names):
    title = "Average daily new cases in the last 7 days per million"
    return plot_trend(y="cases_ac_pm", names=names, title=title)


@app.callback(Output("cases-pm", "figure"), [Input("ids", "value")])
def plot_cases_pm(names):
    title = "Total cases per million"
    return plot_trend(y="cases_pm", names=names, title=title)


@app.callback(Output("tests-ac-pm", "figure"), [Input("ids", "value")])
def plot_tests_ac_pm(names):
    title = "Average daily new tests in the last 7 days per million"
    return plot_trend(y="tests_ac_pm", names=names, title=title)


@app.callback(Output("tests-pm", "figure"), [Input("ids", "value")])
def plot_tests_pm(names):
    title = "Total tests per million"
    return plot_trend(y="tests_pm", names=names, title=title)


@app.callback(Output("deaths-ac-pm", "figure"), [Input("ids", "value")])
def plot_deaths_ac_pm(names):
    title = "Average daily new deaths in the last 7 days per million"
    return plot_trend(y="deaths_ac_pm", names=names, title=title)


@app.callback(Output("deaths-pm", "figure"), [Input("ids", "value")])
def plot_deaths_pm(names):
    title = "Total deaths per million"
    return plot_trend(y="deaths_pm", names=names, title=title)


if __name__ == "__main__":
    app.run_server(debug=True)

