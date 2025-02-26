#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 20:37:54 2021

@author: songyang
"""
import os
import sys

sys.path.insert(0, './pages/scripts')

import dash_bootstrap_components as dbc

from dash import html, dcc, dash_table, Input, Output, State, MATCH, ALL

from dash.exceptions import PreventUpdate
import base64

from app import app, server, register_auth_app

from pages import page_1, page_3, page_4, page_5, page_input_output, page_dbc, page_todo_practice, page_table_edit_db

# Access Control
# from authlib.integrations.requests_client import OAuth2Session
# import requests
# from requests.structures import CaseInsensitiveDict


# Data Mock UP
import numpy as np
import pandas as pd

# %% ===================== SIDEBAR SETTING  ===================================
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

sidebar = html.Div(
    [
        html.H5("Dash", className='d-flex justify-content-center'),
        html.Hr(),
        dbc.Nav(
            [  # Filters
                html.H5(children='Overall Filter', className='card-title'),
                dbc.Row([
                    # Filter 1
                    dbc.Col(html.Label('Filter 1: '), className='card-text ms-3'),
                    dbc.Col(
                        dcc.Dropdown(id='filter_1_dpn',
                                     options=[
                                         {'label': 'option 1', 'value': 'OPTION1'},
                                         {'label': 'option 2', 'value': 'OPTION2'},
                                     ],
                                     value='OPTION1',
                                     multi=False,
                                     style={'font-size': '85%'}
                                     ),
                        width=12
                    ),
                ]),
            ]
        ),
        html.Br(),
        dbc.Nav(
            [

                dbc.NavLink("Simple dropdown and plot", href="/page-1", active="exact"),
                dbc.NavLink("Table Interactivity", href="/page-3", active="exact"),
                dbc.NavLink("Pattern Matching Callback", href="/page-4", active="exact"),
                dbc.NavLink("Pivot Table ", href="/page-5", active="exact"),
                dbc.NavLink("Data I/O ", href="/page-IO", active="exact"),
                dbc.NavLink("Bootstrap Lib ", href="/page-dbc", active="exact"),
                dbc.NavLink('dbc docs', href='https://dash-bootstrap-components.opensource.faculty.ai/docs/components/',
                            active='exact', external_link=True,
                            target='_blank'),
                dbc.NavLink('To-Do List Practice', href="/page-todo-practice", active="exact"),
                dbc.NavLink('Table Edit w DB', href="/page-table-edit-db", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# search bar
search_bar = dbc.Row(
    [
        dbc.Col(dbc.Input(type="search", placeholder="Search")),
        dbc.Col(
            dbc.Button(
                html.I(className="fas fa-search"),
                color="secondary", className="ms-2", n_clicks=0
            ),
            width="auto",
        ),
    ],
    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)



# user info
user_info = dbc.Row(
    [
        dcc.Store(id='username-url', data=''),
        dbc.Col(html.I(className='fas fa-user'), width='auto'),
        dbc.Col(html.Label(children='User Name', id='username', className='mt-1'), width='auto'),
        # dbc.Col(dcc.Link('Log out', href='/logout', className='ms-2'), width='auto'),
    ],
    className='d-flex align-items-center flex-nowrap text-light g-2'
)

# %% ===================== NAVBAR SETTING  ====================================
LOGO_IMG_FILE = r"./assets/img/dash_logo.png"
LOGO_IMG = base64.b64encode(open(LOGO_IMG_FILE, 'rb').read())

navbar = dbc.Navbar(
    dbc.Container(
        [
            # Left-side logo and brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src='data:image/png;base64,{}'.format(LOGO_IMG.decode()), height='35px')),
                    dbc.Col(dbc.NavbarBrand('Dash')),
                ],
                align="center",
                className="g-3",
            ),

            # Right-side search bar and user info (pushed to the right)
            dbc.Row(
                [
                    dbc.Col(search_bar, className='me-1', width=7),  # Search bar
                    dbc.Col(user_info, width='auto')  # User info
                ],
                className="ms-auto d-flex align-items-center",
                align="center",
            )
        ],
        fluid=True
    ),
    color='#0091da',
    dark=True,
)

# %% ===================== CONTENT  ===========================================
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

content = html.Div(id="page-content", style=CONTENT_STYLE)

# %% ===========================================================================

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        html.Div(id='placeholder'),
        dcc.Store(id='data_source_1'),
        dcc.Store(id='db_movie_data'),
        dcc.Store(id='db_movie_data_updated'),
        dcc.Store(id='valid_access_res'),
        sidebar,
        navbar,
        content,
        html.Footer('© 2022 Song Holmes', className='text-center')
    ]
)


# %% Client Callback: to get the visitor username
# app.clientside_callback(
#     '''
# function Get(yourUrl){
#     var Httpreq = new XMLHttpRequest(); // a new request
#     Httpreq.open("GET", yourUrl, false);
#     Httpreq.withCredentials = true;
#     Httpreq.send(null);
#     return Httpreq.responseText.replaceAll('"', '');
#     }

#     ''',
#     Output('username','children'),
#     Input('username-url', 'data')
#     )


# %% Overall callbacks
# @app.callback(
#     Output('valid_access_res', 'data'),
#     Input('username', 'children')
#     )
# def access_valid(username):
#     client_id = '',
#     client_secret = ''
#     token_url = 'https://..xxx.com/token'
#     client = OAuth2Session(client_id, client_secret)
#     allow_access = False

#     token = client.fetch_token(token_url,
#                                grant_type = 'client_credentials',
#                                verify=False)['access_token']
#     username = username.upper()
#     headers = CaseInsensitiveDict()
#     headers['accept'] = 'application/json'
#     headers['Authorization'] = f'Bearer {token}'
#     mt_group_list = ['group 1', 'group 2']
#     for mt_group in mt_group_list:
#         url = f'https//....'
#         resp = requests.get(url, headers = headers, verify = False)
#         if resp.text == '"expected value"':
#             allow_access = True
#             break
#     return allow_access


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/page-1":
        return page_1.layout
    elif pathname == "/page-3":
        return page_3.layout
    elif pathname == "/page-4":
        return page_4.layout
    elif pathname == "/page-5":
        return page_5.layout
    elif pathname == "/page-IO":
        return page_input_output.layout
    elif pathname == "/page-dbc":
        return page_dbc.layout
    elif pathname == "/page-todo-practice":
        return page_todo_practice.layout
    elif pathname == "/page-table-edit-db":
        return page_table_edit_db.layout
    # If the user tries to reach a different page, return a 404 message
    elif pathname == "/logout":
        return dbc.Container([html.H1("Successfully Logout", className="text-danger")]
                             )
    return dbc.Container(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        fluid=True,
        className="py-3",
    )


# Business Callback
@app.callback(
    Output('data_source_1', 'data'),
    Input('placeholder', 'children')
)
def data_transition(_):
    df = pd.DataFrame(data=np.array([[5, 3, 6],
                                     [4, 5, 6]]),
                      columns=['col1', 'col2', 'col3'])

    ## For other part to access the output data
    # data_source_1 = input()
    # if pd.isnull(data_source_1):
    #     PreventUpdate()
    # df = pd.read_json(data_source_1, orient = 'split')

    return df.to_json(date_format='iso', orient='split')


# %% register callback from pages
page_1.register_callback(app)
page_3.register_callback(app)
page_4.register_callback(app)
page_5.register_callback(app)
page_input_output.register_callback(app)
page_dbc.register_callback(app)
page_todo_practice.register_callback(app)
page_table_edit_db.register_callback(app)
register_auth_app(app)

if __name__ == "__main__":
    # Official launched a more neat version for multi-page: https://dash.plotly.com/urls
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # to handle not able to run http
    app.run_server(port=3002, debug=True)
