#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 20:42:24 2021

@author: songyang
"""

import dash
from dash import html, dcc, dash_table, Input, Output, State, MATCH, ALL, ClientsideFunction

import dash_bootstrap_components as dbc

#%% Layouts
layout = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="Toast", tab_id="tab-1"),
                    dbc.Tab(label="Tab 2", tab_id="tab-2"),
                ],
                id="card_dbc_tabs",
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(html.Div(id="card_dbc_content")),
    ]
)

#%% Tab1: Toast ============
tab_1_contents = [
        html.H2(children = 'Toast Feature Examples'),
        html.P(children = '''Toasts are lightweight notifications designed to mimic the push notifications popularized by mobile and desktop operating systems. The Toast component automatically creates a header and body, the children of the component populate the body, while the header property can be used to set the header text.'''),
        dbc.Button(
            "Open toast",
            id="positioned-toast-toggle",
            color="primary",
            n_clicks=0,
        ),
        dbc.Toast(
            "This toast is placed in the top right",
            id="positioned-toast",
            header="Positioned toast",
            is_open=False,
            dismissable=True,
            icon="danger",
            # top: 66 positions the toast below the navbar
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        ),
    ]


#%% Register Callbacks of Components ============
def register_callback(app):
    @app.callback(
        Output("card_dbc_content", "children"),
        [Input("card_dbc_tabs", "active_tab")]
    )
    def tab_content(active_tab):
        if active_tab == 'tab-1':
            return tab_1_contents
        else:
            return None


#%% Tab1: Toast ============
    @app.callback(
        Output("positioned-toast", "is_open"),
        [Input("positioned-toast-toggle", "n_clicks")],
    )
    def open_toast(n):
        if n:
            return True
        return False

    # # This clientside callback will be called once when the element is injected into the DOM and will give
    # # it some javascript event listeners to make it draggable around the viewport.
    # app.clientside_callback(
    #     ClientsideFunction(namespace="clientside", function_name="make_draggable"),
    #     Output("positioned-toast", "className"), # the attribute here will not be updated, it is just used as a dummy
    #     Input("positioned-toast", "is_open"),
    #      State("positioned-toast","id"),
    # )
#%% For Single Page Runnable
if __name__ == '__main__':
    
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    
    app.layout = layout
    register_callback(app)
    
    app.run_server(debug=False, port = 8889)