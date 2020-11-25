import os

import flask
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, Response, flash, \
    sessions
from login import login_api, getFirstName, getUserLoginEmail, setFirstName, setUserLoginEmail, getLastName
from product import product_api
from register import register_api
import pymongo
import hashlib
import re
import jwt
import yaml
from redis import Redis
from flask_session import Session
# from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import timedelta
from functools import wraps
import datetime
import json
from bson import ObjectId, json_util
from flask_bcrypt import Bcrypt
from search import search_api
from flask_login import login_user, login_required, logout_user, current_user

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
db_collection_userlogin = db['OAUTH_USER_DETAILS']
db_collection_product = db['Product']

# dotenv setup
from dotenv import load_dotenv

load_dotenv()

URL = 'http://127.0.0.1:5000/'
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

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": yaml_reader['email_address'],
    "MAIL_PASSWORD": yaml_reader['email_password']
}
app.config.update(mail_settings)
mail = Mail(app)
bcrypt = Bcrypt()
app.add_template_global(getFirstName, 'getFirstName')
app.add_template_global(getLastName, 'getLastName')

app.add_template_global(getUserLoginEmail, 'getUserLoginEmail')

user = ""
token = ""


@app.route('/', methods=['GET'])
def default():
    return render_template("index.html")


@app.route('/home', methods=['GET', 'POST'])
def home_page1():
    return render_template("index.html")


@app.route('/index.html', methods=['GET'])
def home_page2():
    return render_template("index.html")


@app.route('/login', methods=['POST'])
def login():
    google = oauth.create_client('google')
    redirect_url = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_url)


@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
    global token
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

        if db_collection_userlogin.find_one({"email": user_info['email']}) is None:
            db_collection_userlogin.insert_one(user_info)
        setFirstName(user_info['given_name'])
        setUserLoginEmail(user_info['email'])

        token = jwt.encode({'public_id': user_info['email'],
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
        # return {"shreyas":user_info}
        # user = oauth.google.userinfo(token=token)  # uses openid endpoint to fetch user info
        # Here you use the profile/user data that you got and query your database find/register the user
        # and set ur own data in the session not the profile from google
        # session['profile'] = user_info
        # session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
        # return redirect('/')

    session['profile'] = user_info
    session.permanent = True  # make the session permanent so it keeps existing after browser gets closed
    return redirect('/')


def add_JWT():
    return {"x-access-token": token}


def getToken():
    return token


app.add_template_global(getToken, "getToken")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global token
        token = request.args.get("token")
        # if 'x-access-token' not in request.headers:
        #     request.headers['x-access-token'] = token

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = user
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

    # return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


@app.route('/login-result', methods=["POST"])
def login1():
    ajax_json = request.get_json()
    # em, login_password = request.form.get("email"), request.form.get("password")
    em, login_password = ajax_json["email"], ajax_json["password"]
    print(em)
    print(login_password)
    if not em or not login_password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    # user = db_collection_User.find_one({"fullname":auth.username})
    query = {"email": em}
    info = db_collection_User.find_one(query)
    if not info:
        return render_template("login_fail.html")

    if bcrypt.check_password_hash(pw_hash= info['password_hash'],
                                      password=login_password):
        setUserLoginEmail(email=em)
        setFirstName(info['firstname'])
        # print(query)
        global user
        user = json.loads(json_util.dumps(list(db_collection_User.find(query))))
        # print(user)
        # return {"res":json.loads(json_util.dumps(user))}
        # return {"res":user}
        tempOutput = []
        for curr in user:
            tempOutput.append(curr)
        # return {"check":tempOutput}
        # if not user:
        #     return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        global token
        token = jwt.encode(
            {'public_id': tempOutput[0]['password_hash'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'])
        print(token)
        r = {"token":token.decode('ascii')}
        return jsonify(r)
        # return redirect(url_for("default")), {'x-access-token': token}

    return render_template("login_fail.html")


@app.route('/cart', methods=['GET'])
def cart():
    url_decode = jwt.decode(request.args.get("token"), app.config['SECRET_KEY'], algorithms=['HS256'])
    user_info = db_collection_User.find_one({"password_hash": url_decode['public_id']})
    print(user_info['email'])
    return render_template("cart.html")


@app.route('/about', methods=['GET'])
def about():
    return render_template("about.html")


@app.route('/forget-password', methods=['GET', 'POST'])
def email():
    print(email)
    msg = Message("Reset Your MooDairy Password",
                  sender="lincelot97@gmail.com",
                  recipients=[getUserLoginEmail()])
    fname = getFirstName()
    msg.body = "Hello " + fname + "!\n" \
                                  "Thanks for using MooDairy. \n" \
                                  "Maintaining your security is our top priority. \n" \
                                  "Please click the link below to finish resetting your password.\n" \
                                  "http:127.0.0.1:5000/forget_password.html"
    mail.send(msg)
    return 'Sent'

@app.route('/profile-account', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        ajax_json = request.get_json()
        data = ajax_json["data"]

        if data:
            return json.dumps("True")
        else:
            return json.dumps('False')

    if request.method == 'GET':
        if getToken():
            return render_template("profile.html")
        else:
            return render_template("notfound.html")



@app.route('/profile/', methods=['GET', 'POST'])
def funcProfile():
    if request.method == "POST":
        hash_decode = jwt.decode(getToken(),
                                 app.config['SECRET_KEY'],
                                 algorithms=['HS256'])['public_id']
        query = {"password_hash": hash_decode}
        ajax_json = request.get_json()
        if "currentpassword" in ajax_json:
            current_password = ajax_json['currentpassword']
            pwd1 = ajax_json['password1']
            pwd2 = ajax_json['password2']

            if bcrypt.check_password_hash(pw_hash= hash_decode,
                                          password=current_password):
                # verify current user pwd
                # update user new pwd
                update_query = { "$set" : { "password_hash" : bcrypt.generate_password_hash(password=pwd1).decode("utf-8") }}
                db_collection_User.update_one(query, update_query)
                return json.dumps('True')
                return json.dumps('True')
            else:
                return json.dumps('False')

        if "type_name" in ajax_json:
            _type, _name = 0, 1
            new_type_name = ajax_json['type_name']
            if new_type_name[_type] == "First Name":
                update_query = { "$set" : { "firstname" : new_type_name[_name],
                                            "fullname": new_type_name[_name]+
                                                        " "+
                                                        db_collection_User.find_one(query)['lastname'] }}
                db_collection_User.update_one(query, update_query)
                setFirstName(new_type_name[_name])
            else:
                update_query = {"$set": {"lastname": new_type_name[_name],
                                         "fullname": db_collection_User.find_one(query)['lastname']+
                                                     " " +
                                                     new_type_name[_name]
                                         }}
                db_collection_User.update_one(query, update_query)
            return json.dumps("True")

        return json.dumps('True')

@app.route("/log-out", methods=["POST"])
def logout():
    global token
    token = ""
    return json.dumps('True')

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
