#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 20:42:24 2021

@author: songyang
"""

import dash
from dash import html, dcc, dash_table, Input, Output, State, MATCH, ALL


import dash_bootstrap_components as dbc

layout = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="Tab 1", tab_id="tab-1"),
                    dbc.Tab(label="Tab 2", tab_id="tab-2"),
                ],
                id="card-tabs",
                card=True,
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(html.P(id="card-content", className="card-text")),
    ]
)


def register_callback(app):
    @app.callback(
        Output("card-content", "children"), [Input("card-tabs", "active_tab")]
    )
    def tab_content(active_tab):
        return "This is tab {}".format(active_tab)


if __name__ == '__main__':
    
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    
    app.layout = layout
    register_callback(app)
    
    app.run_server(debug=False, port = 8889)