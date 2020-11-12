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
error_msg = ""
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

# @login_api.route('/login-result', methods=['POST'])
# def login():
#     global passing_token
#     _email = request.form.get("email")
#     # _username = request.form.get("username")
#     _password = request.form.get("password")
#     query = {"email": _email}
#     user = json.loads(json_util.dumps(list(db_collection_User.find(query))))
#     # return {"res":json.loads(json_util.dumps(user))}
#     tempOutput=[]
#     for curr in user:
#         tempOutput.append(curr)
#     # return {"check":tempOutput}
#     # if not user:
#     #     return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
#     token = jwt.encode({'public_id' :tempOutput[0]['email'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=5)}, app.config['SECRET_KEY'])
#     # return {"check":token}
#     # token_global=json.loads(token.decode('UTF-8'))
#     token_global=jsonify({'token' : token.decode('UTF-8')})
#     passing_token=str(token.decode('UTF-8'))
#     return {"check":passing_token}
#
#     # return {"check":passing_token}
#     _password = hashlib.md5(_password.encode('utf8')).hexdigest()
#
#     if not _email:
#         return render_template("login_fail.html")
#
#     if _email:
#         if db_collection_User.find_one({"email": _email, "password": _password}):
#             return render_template("index.html")
#         else:
#             return render_template("login_fail.html")
#     return render_template("index.html")


@login_api.route('/login-result', methods=['POST'])
def login():
    _email = request.form.get("email")
    _password = request.form.get("password")

    if not _email:
        setErrorMsg("Empty field.")
        return render_template("login_fail.html")

    if db_collection_User.find_one({"email": _email}):
        user_info = db_collection_User.find_one({"email": _email})
        pwd_hash = user_info['password_hash']
        if bcrypt.check_password_hash(pw_hash=pwd_hash, password=_password):
            fname = user_info['firstname']
            setFirstName(fname)
        else:
            setErrorMsg("Email and password not match.")
            return render_template("login_fail.html")

    else:
        setErrorMsg("Email not exists. Please sign up.")
        return render_template("login_fail.html")

    return render_template("index.html")

def setErrorMsg(msg):
    global error_msg
    error_msg = msg

def getErrorMsg():
    return error_msg

# def getToken():
#     return passing_token