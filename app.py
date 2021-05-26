# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import dash
import dash_bootstrap_components as dbc

FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, FA],
                suppress_callback_exceptions=True)


server = app.server           