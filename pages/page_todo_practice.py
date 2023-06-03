import dash
from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL, Patch
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

app = Dash(__name__)

layout = dbc.Card(
    [
        dbc.CardHeader('Dynamic generate multiple callback function'),
        dbc.CardBody(
            [
                dbc.Row(html.H5('Dash To-Do List')),
                dbc.Row(
                    [
                        dbc.Col(dbc.Input(id='input_todo', placeholder='Input your to do items here'), width=3),
                        dbc.Col(dbc.Button(id='btn_add', children='Add'), width=1),
                        dbc.Col(dbc.Button(id='btn_clear_done', children='Clear Done'), width=2)
                    ]
                ),
                dbc.Row(
                    html.Div(id='div_dropdown_container', children=[])
                ),

            ]

        )
    ]
)


def register_callback(app):
    @app.callback(
        Output('div_dropdown_container', 'children'),
        Output('input_todo', 'value'),
        Input('btn_add', 'n_clicks'),
        State('input_todo', 'value'),
        State('div_dropdown_container', 'children')
    )
    def add_todo_items(n_clicks, input_todo, existed_container):
        if n_clicks is None:
            raise PreventUpdate
        added_content = dbc.Row(
            dbc.Col(
                dcc.Checklist(
                    id={'type': 'added_todo_item', 'index': n_clicks},
                    options=[input_todo]
                ),
            )
        )
        existed_container.append(added_content)
        return existed_container, ''


    @app.callback(
        Output('div_dropdown_container', 'children', allow_duplicate=True),
        Input('btn_clear_done', 'n_clicks'),
        State({'type': 'added_todo_item', 'index': ALL}, 'value'),
        prevent_initial_call=True
    )
    def clear_todo_items(n_clicks, done_status):
        patched_list = Patch()
        done_id_list = []
        for id_, value_ in enumerate(done_status):
            if value_ is not None:
                done_id_list.append(id_)
        # start to delete from the last items, if start from the first will affect the sequence id
        for id_ in reversed(done_id_list):
            del patched_list[id_]
        return patched_list




if __name__ == '__main__':
    FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, FA])
    app.layout = layout
    register_callback(app)
    app.run_server(debug=True, port=8888,)
