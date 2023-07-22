# -*- coding: utf-8 -*-
# https://github.com/googleapis/google-api-python-client
# https://developers.google.com/identity/protocols/oauth2/web-server
# https://stackoverflow.com/questions/45845872/running-a-dash-app-within-a-flask-app
# https://hackersandslackers.com/plotly-dash-with-flask/
# last of https://github.com/plotly/dash/issues/214
# Most close user case: https://dev.to/naderelshehabi/securing-plotly-dash-using-flask-login-4ia2
# Most close user case but in Flask: https://geekyhumans.com/how-to-implement-google-login-in-flask-app/
# Resolve the first issue that sharing the route between flask and dash, but need to settle how to transfer the data
# Furthermore, how to write it to a package rather than a page
# https://stackoverflow.com/questions/52286507/how-to-merge-flask-login-with-a-dash-application

## Midware, check whether user has access token, if not redirect to log in (google login) page,
# otherwise could access dash app
# After get the information, store to database, so that could differentiate user with different access, so when user
# login and get the username, could check the DB for his allowed access or personalized contents

# Use redirect to save the  access token/ (JWToken) into cookie, can just use cookie to verify next time access, whether it is
# valid or not. Can just decode and see if it is not expire yet.
# cookie is stored per origin: schema + host + port? store in frontend
# Session has drawback, since it store the state rather than just decode access code, store in backend, but can always
# check the unique login

#pyjwt to encode/ decode dictionary to this

# strategy pattern: how to design and leverage from one case to a more general template


import os

import dash
from dash import html, dcc, dash_table, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

import dash_bootstrap_components as dbc
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = '../modules/dash_google_auth/client_secret_437209673045-6ck32on6phfnieug14b51ldas2d5i6vi.apps.googleusercontent.com.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email']

layout = dbc.Card(
    [
        dbc.CardHeader('Google Login Test'),
        dbc.CardBody(
            [

                html.Div(
                    [
                        dcc.Location(id='url', refresh=False),
                        dcc.Location(id='redirect', refresh=True),
                        dbc.Button(id='log_in_btn', children='Log In', n_clicks=0),
                        dbc.Button(id='log_out_btn', children='Log Out', n_clicks=0),
                        html.Div(html.H5(id='output', children=''))
                    ], style={'width': '48%', 'display': 'inline-block'}),
            ]
        )
    ]
)


server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.server.secret_key = 'REPLACE ME - this value is here as a placeholder.'
app.layout = layout

@app.callback(
    Output('redirect', 'pathname'),
    Input('log_in_btn', 'n_clicks'),
    prevent_initial_update=True
)
def login(n_clicks):
    if n_clicks > 0:
        return '/authorize'

@app.callback(
    Output('redirect', 'pathname', allow_duplicate=True),
    Input('log_out_btn', 'n_clicks'),
    prevent_initial_call=True
)
def login(n_clicks):
    if n_clicks > 0:
        return '/clear'

@app.server.route('/')
def index():
  return print_index_table()


@app.server.route('/test')
def test_api_request():
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  auth_info = googleapiclient.discovery.build('oauth2','v2',credentials=credentials)

  infos = auth_info.userinfo().get().execute()

  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.jsonify(**infos)


@app.server.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)


@app.server.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))


@app.server.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://oauth2.googleapis.com/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    return('Credentials successfully revoked.' + print_index_table())
  else:
    return('An error occurred.' + print_index_table())


@app.server.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run_server('localhost', 3002, debug=True)