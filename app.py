# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import os
import dash_bootstrap_components as dbc
from dash import Dash, html, Input, Output, dcc, no_update
from dash_auth import OIDCAuth
from flask import session, redirect, url_for, request, render_template
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

app = Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, FA],
                suppress_callback_exceptions=True)

app.title = 'Dash Reports Template'
server = app.server
# Secret key for session management
app.server.secret_key = os.urandom(24)

# Define the email whitelist
EMAIL_WHITELIST = {"songyangholmes@gmail.com", "another_user@example.com"}

# Configure OIDC Authentication
auth = OIDCAuth(
    app,
    secret_key=app.server.secret_key,
    idp_selection_route="/login",
    # If you want a different URL prefix for the auth routes, specify here, e.g. url_prefix="/auth"
)

## if should be mentioned that in OIDCAuth.login_request, there is logic:
# 'if len(self.oauth._registry) == 1: idp = next(iter(self.oauth._clients))', which means if only one provider is
# set, then will skip the login selection part

# Provider 1: Google
google_client_id = os.getenv("GOOGLE_CLIENT_ID")  # Reads from system environment variables
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
# Register Google as the Identity Provider (IdP)
auth.register_provider(
    idp_name="Google",
    client_id=google_client_id,  # Replace with your Google Client ID
    client_secret=google_client_secret,  # Replace with your Google Client Secret
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    authorize_params={"scope": "openid email profile"},
    token_endpoint_auth_method="client_secret_post",
)

@app.server.route("/login", methods=["GET", "POST"])
def login_handler():
    """Handles the /login route for IDP selection."""
    if request.method == "POST":
        idp = request.form.get("idp")
    else:
        idp = request.args.get("idp")

    if idp is not None:
        # This calls the OIDCAuth-generated endpoint named "oidc_login"
        return redirect(url_for("oidc_login", idp=idp))

    return render_template('oidc_login_page.html')


# -------------------------------------------------
# Callback to Enforce Whitelist Check
# -------------------------------------------------
def register_auth_app(app):
    @app.callback(
        Output("url", "pathname"),
        Output("username", "children"),
        Input("placeholder", "children")
    )
    def check_user(_):
        """
        1) If the session user is missing or not in the whitelist,
           return "/login" -> triggers client-side redirect to /login
           and do not update user-info.
        2) If the user is whitelisted, no redirect is triggered, and
           user-info displays the user's email.
        """
        user_info = session.get("user")

        # 1) If not logged in or not whitelisted -> redirect to /login
        if not user_info or user_info.get("email") not in EMAIL_WHITELIST:
            return "/login", no_update

        # 2) Otherwise, show the user email
        email = user_info.get("email", "Unknown Email")
        return no_update, email.split('@')[0]