import os

from flask import Flask, render_template, request, redirect
from login import login_api
from register import register_api
import pymongo
import hashlib
import re
import yaml
from redis import Redis
from flask_session import Session

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


@app.route('/', methods=['GET'])
def default():
    return render_template("index.html")


@app.route('/home', methods=['GET'])
def home_page1():
    return render_template("index.html")


@app.route('/index.html', methods=['GET'])
def home_page2():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5002,
        debug=True
    )

