import os
from flask import Flask, render_template, request, redirect,url_for,session
from login import login_api, getFirstName, setFirstName
from register import register_api
from search import search_api
from product import product_api

from redis import Redis
from flask_session import Session
# from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from datetime import timedelta
import pymongo
import hashlib
import re
import yaml
import os
import requests_oauthlib
import collections


f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.safe_load(data)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config['SECRET_KEY'] = os.urandom(24)
app.register_blueprint(login_api)
app.register_blueprint(register_api)
app.register_blueprint(search_api)
app.register_blueprint(product_api)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client['dairy_user_info']
db_collection_User = db['User']
db_collection_userlogin=db['OAUTH_USER_DETAILS']
db_collection_product=db['Product']

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

productname={
              10002007001:"Product-1",
              10002007002:"Product-2",
              10002007003:"Product-3",
              10002007004:"Product-4",
              10002007005:"Product-5",
              10002007006:"Product-6",
              10002007007:"Product-7",
              10002007008:"Product-8"
            }



app.add_template_global(getFirstName, 'getFirstName')

@app.route('/', methods=['GET'])
def default():
    print(getFirstName())
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
    return google.authorize_redirect(redirect_url)


@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
    if request.method == 'POST':
        fid = request.args.get('fid')  # Your form's
        name = request.args.get('name')
        user_info = {
            "fid": fid,
            "name": name
        }

    else:
        google = oauth.create_client('google')  # create the google oauth client
        token = google.authorize_access_token()  # Access token from google (needed to get user info)
        resp = google.get('userinfo', token=token)  # userinfo contains stuff u specificed in the scrope
        user_info = resp.json()

        if db_collection_userlogin.find_one({"email":user_info['email']}) is None:
            db_collection_userlogin.insert_one(user_info)
        setFirstName(user_info['given_name'])
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




# @app.route("/products.html/<string:tokenvalue>", methods=['GET'])
# def product(tokenvalue):
#     # header=headers
#     # url = base_url
#     # resp = request.post(url=url,header=header)
#     # print(resp)
#     return render_template("products.html")

@app.route('/cart.html', methods=['GET'])
def cart():
    return render_template("cart.html")

@app.route('/about.html', methods=['GET'])
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )

