import json
import os
import sqlite3

# Third-party libraries
from flask import Flask, redirect, request, url_for,render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
import logging
import click

# Internal imports
from db import init_db_command
from user import User


# GOOGLE_CLIENT_ID = os.environ.get("175681250166-qnkr17p6pvp3knl8au2ff4snuism42g1.apps.googleusercontent.com", None)
GOOGLE_CLIENT_ID = "293323576604-8kn5l2954a35268eliajgd4u75dq8gfo.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "8doTyA-giqRWnNbj-rZ87hHx"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

BASE_URL='https://127.0.0.1:5000'

app = Flask(__name__)
app.secret_key = os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except:
    # Assume it's already been created
    pass

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)



@app.route("/")
def index():
    return render_template('login.html')
    # return '<div class="gloginbtn"><a class="button" href="/login">Login with google</a><div>'



@app.route("/userinfo")
def userinfo():
    print(current_user.is_authenticated)
    #print(current_user.name)
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return ' '

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/authorize")
def authorize():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=BASE_URL+ "/token",#request.base_url 
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/token")
def token():
    # Get authorization code Google sent back to you
    code = request.args.get("code")



    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]


    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
   


    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))



    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400


    user = User(
        gid=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # don't store for now
    if not User.get(unique_id):
         User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user to the another page
    return redirect(url_for("index"))






@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(ssl_context="adhoc")
