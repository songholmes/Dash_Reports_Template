#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  5 10:07:32 2022

@author: songyang
"""

import dash
import dash_bootstrap_components as dbc
from collections import OrderedDict
from dash import html, dcc, dash_table, Input, Output, State, MATCH, ALL
import pandas as pd

from logger import Logger
logger = Logger('table.log')

#%% Prepare Filter Functions
operators = [
    ['ge ', '>='],
    ['le ', '<='],
    ['lt ', '<'],
    ['gt ', '>'],
    ['ne ', '!='],
    ['eq ', '='],
    ['contains '],
    ['datestartswith ']
             ]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


#%% Main Function
def gen_table(df,component_id = 'tbl_id',tbl_cols = None, style_data_condi_color = [], export_type = 'csv'):
    
    ## CUSTOMIZED COLUMN NAMES
    if (tbl_cols == None) or (type(tbl_cols)!=list):
        tbl_cols = [{"name": i, "id": i} for i in df.columns]
    else:
        if (type(tbl_cols[0])!=dict):
            tbl_cols = [{"name": i, "id": j} for i,j in zip(tbl_cols, df.columns)]
        else:
            pass # user set-up multi level column
    
    ## STYLE_DATA_CONDITION
    # More details: https://dash.plotly.com/datatable/conditional-formatting
    style_data_condi_base = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(220, 220, 220)',
        }
    ]
    customized_style_data_condition = style_data_condi_base + style_data_condi_color
    
    #%% TABLE SET-UP
    table = dash_table.DataTable(
        data = df.to_dict('records'),
        columns = tbl_cols,
        id = component_id,
        export_format = export_type,
        # fixed_columns={'headers': True}, # fix headers & fix 1st row--> conflict with row_selectable
        editable=True,
        # Filter
        filter_action="custom",
        filter_query='',
        # Sort
        sort_action='custom',
        sort_mode='multi',
        sort_by=[],
        # Row Select
        row_selectable='multi', 
        row_deletable=True,
        selected_rows=[],
        page_action='native',
        page_current= 0,
        page_size= 20,# we have less data in this example, so setting to 20,
        #%% Tooltip
        #   More details: https://dash.plotly.com/datatable/tooltips
        tooltip_header={i: i+"'s tooltip" for i in df.columns},
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df.to_dict('records')
        ],
        tooltip_duration=None,
        #%% Muti-level of Columns,
        # columns need to be {"name": ["City", "Montreal"], "id": "montreal"},
        merge_duplicate_headers=True, 
        #%% Styling
        style_table={
            'height': '500px',
            'overflowY': 'auto',
            'overflowX': 'auto'
            },

        style_data={
          'overflow': 'hidden',
          'textOverflow': 'ellipsis',
          # 'whiteSpace': 'normal',  # open this will eliminate ellipsis
          'height': 'auto',
           'lineHeight': '35px',
           'border': '1px solid grey'
        },
        style_header={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': 0,
            'backgroundColor': 'grey',
            'color':'white', # font color
            'fontWeight': 'bold',
            'border': '1px solid black' 
        },
        style_cell={
        'minWidth': 95, 'maxWidth': 95, 'width': 95,
        },
        #%% Condition Styling
        # style_cell_conditional can override a single column set by style_data
        style_data_conditional = customized_style_data_condition,
        style_cell_conditional=[
            {'if': {'column_id': c }, # Based on real data column names
             'width': '30%', # affected by minWidth in style_cell setting; Can set with '130px'
             'textAlign': 'left'
             }  for c in ['country', 'pop']
        ],
        #%% CSS
        css=[
            # TABLE WISE FORMAT
            {
                'selector': '.dash-spreadsheet td div',
                'rule':'''
                    line-height: 15px;
                    max-height:20px; min-height: 20px; height: 20px;
                    display: block;
                    overflow-y:hidden;
                    overflow: hidden;
                '''
                },
            # TOOLTIP FORMAT
            {
                'selector': '.dash-table-tooltip',
                'rule': 'background-color: grey; font-family: monospace; color: white'
            },
            # HIDE the HIDDEN COLUMN
            {
                'selector':'.show-hide',
                'rule': 'display: none'
                },
            # EXPORT BUTTON STYLE
            {
                'selector': 'button.export',
                'rule':'margin-bottom: 5px; margin-left:5px'
                }
        ],


        )
    
    return table
    


def register_callback(app):
    #%% Table Filter
    # Provide customized filter and sort even pagnize, so that we can have the 
    # intermidiate calculation results
    
    @app.callback(
        Output('tbl_id', "data"),
        Input('tbl_id', "filter_query"),
        Input('tbl_id', 'sort_by'))
    def update_table(filter_query, sort_by):
        ## Sort By
        if len(sort_by):
            dff = df.sort_values(
                [col['column_id'] for col in sort_by],
                ascending=[
                    col['direction'] == 'asc'
                    for col in sort_by
                ],
                inplace=False
            )
        else:
            # No sort is applied
            dff = df
        
        ## Filter Query
        filtering_expressions = filter_query.split(' && ')
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)
    
            if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
                # these operators match pandas series operator method names
                dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
            elif operator == 'contains':
                dff = dff.loc[dff[col_name].str.contains(filter_value)]
            elif operator == 'datestartswith':
                # this is a simplification of the front-end filtering logic,
                # only works with complete fields in standard format
                dff = dff.loc[dff[col_name].str.startswith(filter_value)]
        
        ## Reference: calculate row level subtotal
        # sub = dff.sum(axis = 0)
        # sub[0] = 'Subtotal'
        # sub[1] = '-'
        # sub[2] = '-'
        # dff.loc[dff.index.max()+1] = sub
    
        return dff.to_dict('records')    
    
    
    
    
    #%% Table Operation Extraction
    @app.callback(Output('tbl_out', 'children'),
                  Input('tbl_id', 'derived_viewport_row_ids'),
                  Input('tbl_id', 'selected_row_ids'),
                  Input('tbl_id', 'active_cell'),
                  Input('tbl_id', 'derived_viewport_data')                   
                  )
    def update_graphs(derived_viewport_row_ids,selected_row_ids, active_cell, derived_viewport_data):
        ## ID related stuff will need set a new column called 'id' first, otherwise will be None
        ## row_ids
            # derived_virtual_indices / derived_virtual_row_ids: the order of rows across
            # all pages (for front-end paging) after filtering and sorting.
            
            # derived_viewport_indices / derived_viewport_row_ids: the order of rows on 
            # the currently visible page.
            
        ## data
            # derived_viewport_data/derived_virtual_data
            
        ## selected_rows / selected_row_ids: when row_selectable is enabled and there 
        #  is a checkbox next to each row, these are the selected rows. Note that even
        #  filtered-out or paged-out rows can remain selected.
        
            # derived_virtual_selected_rows / derived_virtual_selected_row_ids: the set 
            # of selected rows after filtering and sorting, across all pages
            
            # derived_viewport_selected_rows / derived_viewport_selected_row_ids: the set
            # of selected rows on the currently visible page.    
            
        ## active_cell: this is the data cell the user has put the cursor on, by
        #  clicking and/or arrow keys. It's a dictionary with keys:
            # - row:       the row index (integer) - may be affected by sorting, filtering,or paging transformations
            # - column:    the column index (integer)
            # - row_id:    the id field of the row, which always stays with it during transformations
            # - column_id: the id field of the column.
        
        if pd.isnull(active_cell):
            return "Click the table"
        else:
            return f'''
        active_cell: {str(active_cell)}======
        selected_row_ids: {selected_row_ids}======
        derived_viewport_row_ids: {derived_viewport_row_ids}=====
        '''









#%% =============================Test Example==================================
if __name__ == '__main__':
    sample_type = 's1'
    customized_cols = None
    customized_data_condi_color = []
    
    #%% Sample 1: multi-rows sample   
    if sample_type == 's1':
        df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
        # add an id column and set it as the index
        # in this case the unique ID is just the country name, so we could have just
        # renamed 'country' to 'id' (but given it the display name 'country'), but
        # here it's duplicated just to show the more general pattern.
        df['id'] = df['country']
        df.set_index('id', inplace=True, drop=False)
        customized_cols = ['Country', 'Pop', 'Continent','LifeExp','GDP_Per_Cap','ID']
        
    #%% Sample 2: long data in the cell
    elif sample_type =='s2':
        data_election = OrderedDict(
            [
                (
                    "Date",
                    [
                        "July 12th, 2013 - July 25th, 2013",
                        "July 12th, 2013 - August 25th, 2013",
                        "July 12th, 2014 - August 25th, 2014",
                    ],
                ),
                (
                    "Election Polling Organization",
                    ["The New York Times", "Pew Research", "The Washington Post"],
                ),
                ("Rep", [1, -20, 3.512]),
                ("Dem", [10, 20, 30]),
                ("Ind", [2, 10924, 3912]),
                (
                    "Region",
                    [
                        "Northern New York State to the Southern Appalachian Mountains",
                        "Canada",
                        "Southern Vermont",
                    ],
                ),
            ]
        )
        df = pd.DataFrame(data_election)
        
    #%% Sample 3: Conditional Formatting
    elif sample_type == 's3':
        data = OrderedDict(
            [
                ("Date", ["2015-01-01", "2015-10-24", "2016-05-10", "2017-01-10", "2018-05-10", "2018-08-15"]),
                ("Region", ["Montreal", "Toronto", "New York City", "Miami", "San Francisco", "London"]),
                ("Temperature", [1, -20, 3.512, 4, 10423, -441.2]),
                ("Humidity", [10, 20, 30, 40, 50, 60]),
                ("Pressure", [2, 10924, 3912, -10, 3591.2, 15]),
            ]
        )
        
        df = pd.DataFrame(data)
        df['id'] = df['Date']
        df.set_index('id', inplace=True, drop=False)
        
        customized_cols = [
        {'name': 'Date', 'id': 'Date', 'type': 'datetime', 'editable': False},
        {'name': 'Delivery', 'id': 'Delivery', 'type': 'datetime'},
        {'name': 'Region', 'id': 'Region', 'type': 'text'},
        {'name': 'Temperature', 'id': 'Temperature', 'type': 'numeric'},
        {'name': 'Humidity', 'id': 'Humidity', 'type': 'numeric'},
        {'name': 'Pressure', 'id': 'Pressure', 'type': 'any'}
        ]
        
        customized_data_condi_color = [
                {
                    'if': {
                        'filter_query': '{{{}}} > {}'.format(col, value),
                        'column_id': col
                    },
                    'backgroundColor': '#ffc7ce',
                    'color': '#9c0006'
                } for (col, value) in df.quantile(0.1).iteritems()
            ] + [
                {
                    'if': {
                        'filter_query': '{{{}}} <= {}'.format(col, value),
                        'column_id': col
                    },
                    'backgroundColor': '#c6efce',
                    'color': '#006100'
                } for (col, value) in df.quantile(0.5).iteritems()
            ]
    
    #%% Dash Page
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    

    app.layout = dbc.Container(
        [
            dbc.Label('Click a cell in the table:'),
            html.Div(gen_table(df,
                               component_id = 'tbl_id',
                               tbl_cols = customized_cols,
                               style_data_condi_color = customized_data_condi_color
                               )
                     ),
            dbc.Alert(id='tbl_out')
            ]
        )
    register_callback(app)
    app.run_server(debug=True, port = 8888)