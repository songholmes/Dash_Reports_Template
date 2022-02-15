#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 22 20:42:24 2021

@author: songyang
"""

# ======================== General Import ====================================
import dash
from dash import html, dcc, dash_table, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

import dash_bootstrap_components as dbc


import base64
import datetime
import io

from PIL import Image
import re

# ======================== Pytorch Import ====================================

# from __future__ import print_function, division
import os




# Ignore warnings
import warnings
warnings.filterwarnings("ignore")


#%% ===========================================================================
# # Class Defined
# =============================================================================



#%% ===========================================================================
# # Function Defined
# =============================================================================

# convert input base64 image to image which pytorch can identify

def base64_to_image(base64_str, image_path=None):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = io.BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img

#%% ===========================================================================
# # UI Layout
# =============================================================================
tab1 = [
        
        dbc.Row(
            [   
                dbc.Col(
                        dbc.Card(
                            [ 
                                 dbc.CardHeader('Sample Images Download'),
                                 dbc.CardBody(
                                     [
                                         html.H6(children = '''Below are ants and bees sample images, you can download them or use your
                                                 own images'''),
                                         html.Button("Download Image", id="btn_image"),
                                         dcc.Download(id="download_image")
                                         ]
                                     )  
                                 ]
                            
                            ), width = 12
                        )
                ]
            ),
        html.Br(),
        html.Br(),
        dbc.Row(
            [   
                dbc.Col(
                        dbc.Card(
                            [ 
                                 dbc.CardHeader('Please upload your Ants or Bees images to classify'),
                                 dbc.CardBody(
                                     [
                                         html.H6(children = '''Click the below button to upload the images which you want to 
                                                 classify'''),
                                         dcc.Upload(id = 'upload-image',
                                                    children = html.Button('Upload File'),
                                                    multiple=True
                                                    ),
                                         dbc.Row(id='output-image-upload')
                                         ]
                                     )  
                                 ]
                            
                            ), width = 12
                        )
                ]
            ),
        html.Br(),
        html.Br(),

        ]

tab2 = html.Div('More Components or Data Here If Needed')




layout = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(label="Image Classifier", tab_id="tab-1"),
                    dbc.Tab(label="More", tab_id="tab-2"),
                ],
                id="card-tabs",
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(html.P(id="tab-card-content", className="card-text")),
    ]
)



#%% ===========================================================================
# # Callback Defined
# =============================================================================





def register_callback(app):
    
    @app.callback(
        Output("tab-card-content", "children"), [Input("card-tabs", "active_tab")]
    )
    def tab_content(active_tab):
        if  active_tab == 'tab-1':
            return tab1
        elif active_tab =='tab-2':
            return tab2
    
    @app.callback(
        Output("download_image", "data"),
        Input("btn_image", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_sample_images(n_clicks):
        return dcc.send_file(
            "./assets/classification_image_samples.zip"
        )
    

    @app.callback(Output('output-image-upload', 'children'),
                  Input('upload-image', 'contents'),
                  State('upload-image', 'filename'))
    def update_output(list_of_contents, list_of_names):
        if list_of_contents is None:
            raise PreventUpdate()
       
        
        if list_of_contents is not None:
            image_file_list = list(map(base64_to_image, list_of_contents))
            image_file_name = list_of_names
            display_results = []
            for i in range(len(list_of_names)):
                display_results.append(dbc.Col(
                        [   
                            html.P(children = image_file_name[i]),
                            html.Img(src=list_of_contents[i], 
                                     style={'max-width':'100%', 'max-height':'300px'}),
                            html.Hr()
                    ], width = 3)
                    )

            return display_results
                
    
    




#%% Main Script

if __name__ == '__main__':
    
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA],
                    suppress_callback_exceptions=True)
    
    app.layout = layout
    register_callback(app)
    
    app.run_server(debug=False, port = 3000) 