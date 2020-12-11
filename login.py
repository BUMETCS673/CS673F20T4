from flask import Blueprint, render_template, request, jsonify, json
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
lastname = ""
error_msg = ""
passing_token = ""
user_login_email = ""
def setFirstName(name):
    global firstname
    firstname = name
    return ""

def getFirstName():
    return firstname


def getLastName():
    return db_collection_User.find_one({"email":getUserLoginEmail()})['lastname']

def setUserLoginEmail(email):
    global user_login_email
    user_login_email = email
    return ""

def getUserLoginEmail():
    return user_login_email

@login_api.route("/login1", methods=['GET'])
def login_page():
    return render_template("login.html", firstname = "")


@login_api.route("/login.html", methods=['GET'])
def login_page1():
    return render_template("login.html")

@login_api.route("/login-fail", methods=['GET'])
def login_page2():
    return render_template("login_fail.html")



# @login_api.route('/login-result', methods=['POST'])
# def login():
#     _email, _password = request.form.get("email"), request.form.get("password")
#     if not _email:
#         setErrorMsg("Empty field.")
#         return render_template("login_fail.html")
#
#     userFind = db_collection_User.find_one({"email": _email})
#     if userFind:
#         user_info = userFind
#         pwd_hash = user_info['password_hash']
#         if bcrypt.check_password_hash(pw_hash=pwd_hash, password=_password):
#             fname = user_info['firstname']
#             db_email = user_info['email']
#             setFirstName(fname)
#             setUserLoginEmail(db_email)
#         else:
#             setErrorMsg("Email and password not match.")
#             return render_template("login_fail.html")
#
#     else:
#         setErrorMsg("Email not exists. Please sign up.")
#         return render_template("login_fail.html")
#
#     return render_template("index.html")

@login_api.route("/forget_password.html", methods = ["GET"])
def forgetPWD():
    return render_template("forget_password.html")

@login_api.route("/reset-password", methods = ["POST"])
def reset():
    pwd = request.form.get("resetpwd")
    pwd2 = request.form.get("resetpwd2")
    _email = getUserLoginEmail()
    if pwd == pwd2 and _email:
        new_hashed_password = bcrypt.generate_password_hash(pwd).decode("utf-8")
        query = {"email": _email}
        db_collection_User.update_one(query, { "$set": {"password_hash" : new_hashed_password}})
        return render_template("reset_success.html")

    else:
        return "Error!"



def setErrorMsg(msg):
    global error_msg
    error_msg = msg

def getErrorMsg():
    return error_msg

# def getToken():
#     return passing_token