import os
import collections
from flask import Flask, render_template, request, redirect,url_for,session,jsonify
from login import login_api, getFirstName
from register import register_api
from search import search_api
from flask_mail import Mail
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

f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.load(data)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
app.config['SECRET_KEY'] = os.urandom(24)
app.register_blueprint(login_api)
app.register_blueprint(register_api)
app.register_blueprint(search_api)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client['dairy_user_info']
db_collection_User = db['User']
db_collection_userlogin=db['OAUTH_USER_DETAILS']
db_collection_product=db['Product']

# dotenv setup
from dotenv import load_dotenv
load_dotenv()

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

@app.route('/authorize',methods=['GET'])
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo',token=token)  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    db_collection_userlogin.insert_one(user_info)
    # user = oauth.google.userinfo(token=token)  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/')

@app.route('/products.html', methods=['GET'])
def product():
    # click product, query db and show all items
    Product_Dictionary = collections.defaultdict(dict)
    for each_product in db_collection_product.find({}):
        _id = str(each_product['_id'])
        Product_Dictionary[_id] = each_product
    return render_template("products.html", product_dict = Product_Dictionary)

@app.route('/cart.html', methods=['GET'])
def cart():
    return render_template("cart.html")

@app.route('/about.html', methods=['GET'])
def about():
    return render_template("about.html")
# def database_retrieval(to_be_checked):
#     query = {"_id":to_be_checked}
#     docs_list = list(db_collection_product.find(query))
#     tempOutput=[]
#     for curr in docs_list:
#         tempOutput.append(curr)
#     headerOutput=[]
#     valueOutput=[]
#     for temp in tempOutput[0]:
#         if temp!="_id":
#             headerOutput.append(temp)
#             valueOutput.append(tempOutput[0][temp])
#     res_product=productname[to_be_checked]
#     print(headerOutput)
#     print(valueOutput)
#     return render_template("product.html",headerOutput=headerOutput,valueOutput=valueOutput,res_product=res_product)
# #
# @app.route('/product1', methods=['GET'])
# def product1():
#     to_be_checked=10002007001
#     return database_retrieval(to_be_checked)
#
# @app.route('/product2', methods=['GET'])
# def product2():
#     to_be_checked=10002007002
#     return database_retrieval(to_be_checked)
#
# @app.route('/product3', methods=['GET'])
# def product3():
#     to_be_checked=10002007003
#     return database_retrieval(to_be_checked)
#
# @app.route('/product4', methods=['GET'])
# def product4():
#     to_be_checked=10002007004
#     return database_retrieval(to_be_checked)
#
# @app.route('/product5', methods=['GET'])
# def product5():
#     to_be_checked=10002007005
#     return database_retrieval(to_be_checked)
#
# @app.route('/product6', methods=['GET'])
# def product6():
#     to_be_checked=10002007006
#     return database_retrieval(to_be_checked)
#
# @app.route('/product7', methods=['GET'])
# def product7():
#     to_be_checked=10002007007
#     return database_retrieval(to_be_checked)
#
# @app.route('/product8', methods=['GET'])
# def product8():
#     to_be_checked=10002007008
#     return database_retrieval(to_be_checked)



if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )