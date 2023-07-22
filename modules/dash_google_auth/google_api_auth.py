import os

import flask
import requests
from flask import make_response
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from .auth import Auth

COOKIE_EXPIRY = 60 * 60 * 24 * 14
COOKIE_AUTH_USER_NAME = 'AUTH-USER'
COOKIE_AUTH_ACCESS_TOKEN = 'AUTH-TOKEN'

AUTH_STATE_KEY = 'auth_state'

# So basically follow the logic described in: https://realpython.com/flask-google-login/
# Dash auth will keep the app to redirect to log in page, if it is not authorized,
# login_request will construct authorized url, post to this url, we will get the response in the callback
# which will pass us code, state and also token. we can save this login info based on the response

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
# CLIENT_SECRETS_FILE = './client_secret_437209673045-6ck32on6phfnieug14b51ldas2d5i6vi.apps.googleusercontent.com.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email']



## Can try to set cookie to direct the username and login info??
## index_auth_wrapper should play the main role to either show index page or authorized and show rest


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

class GoogleAPIAuth(Auth, ):
    def __init__(self, app, credential_secret_file):
        Auth.__init__(self, app)
        self.csf = credential_secret_file
        app.server.config['SECRET_KEY'] = 'REPLACE ME - this value is here as a placeholder.'
        app.server.config['SESSION_TYPE'] = 'filesystem'
        app.server.config["SESSION_PERMANENT"] = False


        @app.server.route('/oauth2callback')
        def oauth2callback():
            return self.login_callback()


        # @app.server.route('/logout')
        # def logout():
        #     return self.logout()

    def is_authorized(self):
        return 'credentials' in flask.session

    def login_request(self):
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.csf, scopes=SCOPES)

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

    def auth_wrapper(self, f):
        def wrap(*args, **kwargs):
            if not self.is_authorized():
                return flask.Response(status=403)

            response = f(*args, **kwargs)
            return response

        return wrap

    def index_auth_wrapper(self, original_index):
        def wrap(*args, **kwargs):
            if self.is_authorized():
                return original_index(*args, **kwargs)
            else:
                return self.login_request()

        return wrap

    def login_callback(self):
        if 'error' in flask.request.args:
            if flask.request.args.get('error') == 'access_denied':
                return 'You denied access.'
            return 'Error encountered.'

        if 'code' not in flask.request.args and 'state' not in flask.request.args:
            print('state not in flask.request.args')
            return self.login_request()
        else:
            # Specify the state when creating the flow in the callback so that it can be
            # verified in the authorization server response.
            state = flask.session['state']

            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                self.csf, scopes=SCOPES, state=state)
            flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

            # Use the authorization server's response to fetch the OAuth 2.0 tokens.
            authorization_response = flask.request.url
            flow.fetch_token(authorization_response=authorization_response)

            # Store credentials in the session.
            # ACTION ITEM: In a production app, you likely want to save these
            #              credentials in a persistent database instead.
            credentials = flow.credentials
            flask.session['credentials'] = credentials_to_dict(credentials)
            return flask.redirect('/')




    @staticmethod
    def logout():
        if 'credentials' in flask.session:
            # Step 1 revoke the token
            credentials = google.oauth2.credentials.Credentials(
                **flask.session['credentials'])
            revoke = requests.post('https://oauth2.googleapis.com/revoke',
                                   params={'token': credentials.token},
                                   headers={'content-type': 'application/x-www-form-urlencoded'})

            # Step 2 delete current session credential
            del flask.session['credentials']
            flask.session.clear()

            status_code = getattr(revoke, 'status_code')
            if status_code == 200:
                print('Crednetial Successfully Revoked')
                return flask.redirect('/')
