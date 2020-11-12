from flask import Blueprint, render_template, request,jsonify
from flask import Flask
import pymongo
import hashlib
import yaml
import json
import jwt 
from bson import ObjectId,json_util
import datetime
import os

login_api = Blueprint('login_api', __name__)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.load(data)

client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]


@login_api.route("/login1", methods=['GET'])
def login_page():
    return render_template("login.html")


@login_api.route("/login.html", methods=['GET'])
def login_page1():
    return render_template("login.html")

@login_api.route('/login-result', methods=['POST'])
def login():
    _email = request.form.get("email")
    # _username = request.form.get("username")
    _password = request.form.get("password")
    query = {"email": _email}
    user = json.loads(json_util.dumps(list(db_collection_User.find(query))))
    # return {"res":json.loads(json_util.dumps(user))}
    tempOutput=[]
    for curr in user:
        tempOutput.append(curr) 
    
    # return {"check":tempOutput}
    # if not user:
    #     return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    token = jwt.encode({'public_id' :tempOutput[0]['email'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=5)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token.decode('UTF-8')})

    _password = hashlib.md5(_password.encode('utf8')).hexdigest()

    if not _email:
        return render_template("login_fail.html")

    if _email:
        if db_collection_User.find_one({"email": _email, "password": _password}):
            return render_template("login_success.html")
        else:
            return render_template("login_fail.html")

    return render_template("index.html")
