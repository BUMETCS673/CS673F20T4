from flask import Blueprint, render_template, request
from flask_bcrypt import Bcrypt
import pymongo

import yaml
import jwt

login_api = Blueprint('login_api', __name__)
bcrypt = Bcrypt()
f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.safe_load(data)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]


firstname = ""

def setFirstName(name):
    global firstname
    firstname = name
    return ""

def getFirstName():
    return firstname

@login_api.route("/login1", methods=['GET'])
def login_page():
    return render_template("login.html", firstname = "")


@login_api.route("/login.html", methods=['GET'])
def login_page1():
    return render_template("login.html")

@login_api.route('/login-result', methods=['POST'])
def login():
    _email = request.form.get("email")
    _password = request.form.get("password")

    if not _email:
        return render_template("login_fail.html")

    if _email:
        if db_collection_User.find_one({"email": _email}):
            user_info = db_collection_User.find_one({"email": _email})
            pwd_hash = user_info['password_hash']
            if bcrypt.check_password_hash(pw_hash=pwd_hash, password=_password):
                # success, find username
                fname = user_info['firstname']
                setFirstName(fname)
                return render_template("index.html", firstname = fname)
            else:
                # Email and password not match!
                return render_template("login_fail.html")

        else:
            return render_template("login_fail.html")

    return render_template("index.html")
