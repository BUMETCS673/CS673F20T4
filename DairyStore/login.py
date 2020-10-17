from flask import Blueprint, render_template, request
import pymongo
import hashlib
import yaml

login_api = Blueprint('login_api', __name__)

f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.load(data)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]


@login_api.route("/login", methods=['GET'])
def login_page():
    return render_template("login.html")


@login_api.route('/login-result', methods=['POST'])
def login():
    _email = request.form.get("email")
    _username = request.form.get("username")
    _password = request.form.get("password")

    _password = hashlib.md5(_password.encode('utf8')).hexdigest()

    if not _email and not _username:
        return render_template("login_fail.html")

    if _email:
        if db_collection_User.find_one({"email": _email, "password": _password}):
            return render_template("login_success.html")
        else:
            return render_template("login_fail.html")

    if _username:
        if db_collection_User.find_one({"username": _username, "password": _password}):
            return render_template("login_success.html")
        else:
            return render_template("login_fail.html")

    return render_template("login.html")
