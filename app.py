# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import dash
import dash_bootstrap_components as dbc
from modules.dash_google_auth.google_api_auth import GoogleAPIAuth

FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, FA],
                suppress_callback_exceptions=True)

app.title = 'Dash Reports Template'
server = app.server

auth_app = GoogleAPIAuth(
    app,
    credential_secret_file='./assets/client_secret_437209673045-6ck32on6phfnieug14b51ldas2d5i6vi.apps.googleusercontent.com.json'
)