import os
from flask import Flask, render_template, request, redirect,url_for,session
from login import login_api
from register import register_api
import pymongo
import hashlib
import re
import yaml
from redis import Redis
from flask_session import Session
# from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta

import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.load(data)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config['SECRET_KEY'] = os.urandom(24)
app.register_blueprint(login_api)
app.register_blueprint(register_api)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client['dairy_user_info']
db_collection_User = db['User']
db_collection_userlogin=db['OAUTH_USER_DETAILS']

# dotenv setup
from dotenv import load_dotenv
load_dotenv()


URL ='http://127.0.0.1:5000/'
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="510040117441-bhjkhpcm8r1l1skiaj6auagd7g0titpf.apps.googleusercontent.com",
    client_secret="Vuw2wpmvi7teEqEGWrOXneF2",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    # userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


FB_CLIENT_ID = '130193744280198'
FB_CLIENT_SECRET = '54432f153c538026224ea90a07809b37'

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]


@app.route('/', methods=['GET'])
def default():
    return render_template("index.html")


@app.route('/home', methods=['GET', 'POST'])
def home_page1():
    return render_template("index.html")


@app.route('/index.html', methods=['GET'])
def home_page2():
    return render_template("index.html")

@app.route('/login',methods=['POST'])
def login():
    google=oauth.create_client('google')
    redirect_url=url_for('authorize',_external=True)
    # code = request.args.get("code")
    return google.authorize_redirect(redirect_url)







@app.route('/authorize',methods=['GET','POST'])
def authorize():
    
    if request.method == 'POST':
        fid = request.args.get('fid') # Your form's
        name = request.args.get('name') 
        user_info={
            "fid":fid,
            "name":name
        }

    else:
        google = oauth.create_client('google')  # create the google oauth client
        token = google.authorize_access_token()  # Access token from google (needed to get user info)
        resp = google.get('userinfo',token=token)  # userinfo contains stuff u specificed in the scrope
        user_info = resp.json()
        db_collection_userlogin.insert_one(user_info)
        # return {"shreyas":user_info}
        # user = oauth.google.userinfo(token=token)  # uses openid endpoint to fetch user info
        # Here you use the profile/user data that you got and query your database find/register the user
        # and set ur own data in the session not the profile from google
        # session['profile'] = user_info
        # session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
        # return redirect('/')

    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')



if __name__ == '__main__':
    print('hello')
    app.run(
        ssl_context="adhoc",
        host='127.0.0.1',
        port=5000,
        debug=True
    )


