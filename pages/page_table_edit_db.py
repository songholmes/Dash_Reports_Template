#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
from dash import html, dcc, dash_table, Input, Output, State, MATCH, ALL, no_update, ctx
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px
import sqlite3 as sl

import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import os

db_file_path = os.path.join(os.getcwd(), 'data', 'tutorial.db')
print(f'Current db file location: {db_file_path}')
if not os.path.exists(db_file_path):
    from pages.scripts.generate_initial_db import get_initial_db
    print(f'Create new db file in {db_file_path}')
    get_initial_db(db_path=db_file_path)

defaultColDef_ = {"flex": 1, "minWidth": 150, "editable": True}
dashGridOptions_ = {'pagination': False, "rowSelection": "multiple",
                    'undoRedoCellEditing': True,
                    'undoRedoCellEditingLimit': 20}

layout = dbc.Card(
    [
        dbc.CardHeader('Table Editor with DB'),
        dbc.CardBody([
            html.H5('Movie Table'),
            dbc.Button("Download CSV", id="csv_download_btn", n_clicks=0, color='secondary', class_name='mb-2'),
            dbc.Row(
                dbc.Col(
                    dag.AgGrid(
                        id="movie_ag_table",
                        className="ag-theme-balham",
                        columnSize="sizeToFit",
                        style={'height': '250px'},
                        dashGridOptions=dashGridOptions_,
                        defaultColDef=defaultColDef_,
                        csvExportParams={
                            "fileName": "ag_grid_test.csv",
                        },
                    ), width=6
                )
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button("Add a Row", id='add_row_btn', outline=True, n_clicks=0,
                                   color='success', size="sm"),
                        width=1, class_name='me-1 mt-2'
                    ),
                    dbc.Col(
                        dbc.Button("Delete Rows", id='delete_row_btn', outline=True, n_clicks=0,
                                   color='danger', size="sm"),
                        width=2, class_name='mt-2')
                ], align='left'
            ),
            dbc.Row(
                dbc.Col(
                    dbc.Button('Update to DB', id='update_db_btn', color='secondary', n_clicks=0, class_name='mt-2'),
                    width=2
                )
            )

        ])
    ]
)


def register_callback(app):
    @app.callback(
        Output('db_movie_data', 'data'),
        Input('placeholder', 'children'),
        Input('db_movie_data_updated', 'data'),
    )
    def load_db_movie_data(_, is_table_updated):
        try:
            con = sl.connect(db_file_path)
            df = pd.read_sql("select * from movie", con)
            con.close()

            return df.to_json(date_format='iso', orient='split')
        except:
            PreventUpdate

    @app.callback(
        Output('movie_ag_table', 'rowData'),
        Output('movie_ag_table', 'columnDefs'),
        Input('db_movie_data', 'data')
    )
    def update_table_from_db(movie_data):
        if pd.isnull(movie_data):
            PreventUpdate()
        df_read = pd.read_json(movie_data, orient='split')
        row_data = df_read.to_dict('records')
        # Method 1: Initialize Columns:
        # column_defs = [{'field': i, 'headerName': i, 'filter': True, 'sortable': True}
        #                for i in df_read.columns]

        # Method 2: Initialize columns manually:
        column_defs = [{'field': 'title', 'headerName': 'Title', 'filter': True, 'sortable': True},
                       {'field': 'year', 'headerName': 'Year'},
                       {'field': 'score', 'headerName': 'Score', }
                       ]

        return row_data, column_defs

    @app.callback(
        Output('movie_ag_table', 'deleteSelectedRows'),
        Output('movie_ag_table', 'rowData', allow_duplicate=True),
        Input('add_row_btn', 'n_clicks'),
        Input('delete_row_btn', 'n_clicks'),
        State('movie_ag_table', 'rowData'),
        prevent_initial_call=True
    )
    def add_or_delete_rows(n_add, n_delete, data):
        if ctx.triggered_id == 'add_row_btn':
            new_row = {
                'title': [''],
                'year': [''],
                'score': ['']
            }
            updated_table = pd.concat([pd.DataFrame(data), pd.DataFrame(new_row)])
            return False, updated_table.to_dict("records")
        elif ctx.triggered_id == 'delete_row_btn':
            return True, no_update

    @app.callback(
        Output('db_movie_data_updated', 'data'),
        Input('update_db_btn', 'n_clicks'),
        State('movie_ag_table', 'rowData'),
        prevent_initial_call=True
    )
    def update_add_delete_actions_to_db(n_clicks, updated_data):
        if n_clicks > 0:
            con = sl.connect(db_file_path)
            df = pd.DataFrame(updated_data)
            df.to_sql('movie', con, if_exists='replace', index=False)

            return True

    @app.callback(
        Output('movie_ag_table', 'exportDataAsCsv'),
        Input('csv_download_btn', 'n_clicks'),
    )
    def export_data_as_csv(n_clicks):
        if n_clicks:
            return True
        return False


if __name__ == '__main__':
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])

    app.layout = layout
    register_callback(app)

    app.run_server(debug=False, port=8888)
