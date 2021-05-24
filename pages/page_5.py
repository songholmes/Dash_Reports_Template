#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 24 19:42:56 2021

@author: songyang
"""

import dash
from dash.dependencies import Input, Output
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH, ALL
import dash_pivottable


layout = dbc.Card(
    [   
         dbc.CardHeader('Pivot Table Plugin'),
         dbc.CardBody(
                     [
                         dbc.NavLink("Reference Link", href="https://community.plotly.com/t/dash-pivottable-released/43333", 
                                     active="exact",
                                     external_link = True,
                                     target='_blank'),
                         html.Hr(),
                         dash_pivottable.PivotTable(
                                data=[
                                    ['Animal', 'Count', 'Location'],
                                    ['Zebra', 5, 'SF Zoo'],
                                    ['Tiger', 3, 'SF Zoo'],
                                    ['Zebra', 2, 'LA Zoo'],
                                    ['Tiger', 4, 'LA Zoo'],
                                ],
                                cols=["Animal"],
                                rows=["Location"],
                                vals=["Count"]
                            )
                         ]
             
             )
    ]
    )


def register_callback(app):
    
    return
    

if __name__ == '__main__':
        
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    app.layout = layout
    register_callback(app)
    app.run_server(debug=False, port = 8888)