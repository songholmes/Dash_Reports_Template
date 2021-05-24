#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Sun May 23 17:32:00 2021

@author: songyang
"""
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd


layout = dbc.Card(
    [   
         dbc.CardHeader('Dynamic generate multiple callback function'),
         dbc.CardBody(
             [  
                dbc.Button("Add Filter", id="dynamic-add-filter", n_clicks=0),
                html.Hr(),
                html.Div(id='dynamic-dropdown-container', children=[]),
                 ]
             
             )
    ]
    )



def register_callback(app):
    @app.callback(
        Output('dynamic-dropdown-container', 'children'),
        Input('dynamic-add-filter', 'n_clicks'),
        State('dynamic-dropdown-container', 'children'))
    def display_dropdowns(n_clicks, children):
        new_element = html.Div([
            dcc.Dropdown(
                id={
                    'type': 'dynamic-dropdown',
                    'index': n_clicks
                },
                options=[{'label': i, 'value': i} for i in ['NYC', 'MTL', 'LA', 'TOKYO']]
            ),
            html.Div(
                id={
                    'type': 'dynamic-output',
                    'index': n_clicks
                }
            )
        ])
        children.append(new_element)
        return children
    
    
    @app.callback(
        Output({'type': 'dynamic-output', 'index': MATCH}, 'children'),
        Input({'type': 'dynamic-dropdown', 'index': MATCH}, 'value'),
        State({'type': 'dynamic-dropdown', 'index': MATCH}, 'id'),
    )
    def display_output(value, id):
        return html.Div('Dropdown {} = {}'.format(id['index'], value))





if __name__ == '__main__':
        
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    app.layout = layout
    register_callback(app)
    app.run_server(debug=False, port = 8888)