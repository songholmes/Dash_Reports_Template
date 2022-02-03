#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 20:37:54 2021

@author: songyang
"""

import sys
sys.path.insert(0, './pages/scripts')

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import base64

from app import app, server

from pages import page_1, page_2, page_3, page_4, page_5, page_input_output




#%% ===================== SIDEBAR SETTING  ===================================
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
        html.H5("Dash", className = 'd-flex justify-content-center'),
        html.Hr(),
        dbc.Nav(
            [
                    
                dbc.NavLink("Simple dropdown and plot", href="/page-1", active="exact"),
                dbc.NavLink("Multiple Tab", href="/page-2", active="exact"),
                dbc.NavLink("Table Interactivity", href="/page-3", active="exact"),
                dbc.NavLink("Pattern Matching Callback", href="/page-4", active="exact"),
                dbc.NavLink("Pivot Table ", href="/page-5", active="exact"),
                dbc.NavLink("Data I/O ", href="/page-IO", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style = SIDEBAR_STYLE,
)

# search bar
search_bar = dbc.Row(
    [
         dbc.Col(dbc.Input(type = 'search', placeholder = 'Search')),
         dbc.Col(
             dbc.Button(
                         html.Span(
                             [ 
                                 html.I(
                                     className="fas fa-search")
                                 ]
                             ), color = 'secondary', className='ml-2'
                         ),width='auto'
             ),
         ],
    no_gutters = True,
    className = 'ml-auto flex-nowrap mt-3 mt-md-0',
    align = 'center'
    )
 
# user info
user_info = dbc.Row(
    [   dcc.Store(  
            id = 'username-url',
            data = ''),
        html.I(
            className = 'fas fa-user mr-2 ml-2'),
        html.Label(
            children = 'User Name',
            id = 'username',
            className = 'mt-2'
            )
      ],
    className = 'ml-2 mr-2 d-flex align-content-center align-items-center flex-wrap text-light'
    )

#%% ===================== NAVBAR SETTING  ====================================
LOGO_IMG_FILE = r"./assets/img/dash_logo.png"
LOGO_IMG = base64.b64encode(open(LOGO_IMG_FILE, 'rb').read())

navbar = dbc.Navbar(
    [
         dbc.Row(
                 [
                      dbc.Col(html.Img(src = 'data:image/png;base64,{}'.format(LOGO_IMG.decode()),
                                       height = '35px', className = 'd-flex justify-content-center mr-3')),
                     dbc.Col(dbc.NavbarBrand('Dash', className = 'ml-3'))
                     ],
                 no_gutters = True,
                 className = 'ml-4 flex-nowrap mt-3 mt-md-0'
             ),
             
         # search bar
         search_bar,
         
         # user_info
         user_info
     ],
    color = '#0091da',
    dark = True
    )

#%% ===================== CONTENT  ===========================================
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


content = html.Div(id="page-content", style=CONTENT_STYLE)

#%% ===========================================================================

app.layout = html.Div(
    [
         dcc.Location(id="url"),
         sidebar,
         navbar,
         content,
         ]
    )

#%% ===========================================================================
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    print('I am here')
    if pathname == "/":
        return html.P("This is the content of the home page!")
    elif pathname == "/page-1":
        return page_1.layout
    elif pathname == "/page-2":
        return page_2.layout
    elif pathname == "/page-3":
        return page_3.layout
    elif pathname == "/page-4":
        return page_4.layout
    elif pathname == "/page-5":
        return page_5.layout
    elif pathname == "/page-IO":
        return page_input_output.layout
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )
page_1.register_callback(app)
page_2.register_callback(app)
page_3.register_callback(app)
page_4.register_callback(app)
page_5.register_callback(app)
page_input_output.register_callback(app)

if __name__ == "__main__":
    app.run_server(port=3001, debug = False)