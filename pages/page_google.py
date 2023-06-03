import os
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google

# Replace with your own client ID and secret from Google Cloud Platform
GOOGLE_CLIENT_ID = '437209673045-6ck32on6phfnieug14b51ldas2d5i6vi.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'

server = Flask(__name__)
server.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersekrit")
server.config["GOOGLE_OAUTH_CLIENT_ID"] = GOOGLE_CLIENT_ID
server.config["GOOGLE_OAUTH_CLIENT_SECRET"] = GOOGLE_CLIENT_SECRET

google_bp = make_google_blueprint(scope=["profile", "email"])
server.register_blueprint(google_bp, url_prefix="/login")

app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='content')
])

index_page = html.Div([
    dbc.Button("Login with Google", id="google-login-button", className="btn-lg",
               href="/login/google", external_link=True)
])

main_page = html.Div([
    html.H1('Welcome! You are logged in.'),
    html.Div(id='user-email'),
    dbc.Button("Logout", id="logout-button", className="btn-lg", href="/logout")
])


@app.callback(Output('content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if not google.authorized:
        return index_page

    if pathname == '/':
        return main_page

    return html.H1('Page not found'), 404


@app.server.route("/logout")
def logout():
    token = google.token["access_token"]
    resp = google.post("https://accounts.google.com/o/oauth2/revoke",
                       params={"token": token},
                       headers={"Content-Type": "application/x-www-form-urlencoded"})

    if resp.ok:
        del google.token
        return redirect("http://127.0.0.1:8050/_dash-login")
    else:
        return "Failed to log out", 400


if __name__ == '__main__':
    app.run_server(debug=True)
