from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from login import setFirstName, getFirstName, setUserLoginEmail
from flask_session import Session
import pymongo
import hashlib
import yaml
import re
import datetime

from redis import Redis

register_api = Blueprint('register_api', __name__)
bcrypt = Bcrypt()
f = open("flask_yaml/mongo-credential.yaml")
data = f.read()
yaml_reader = yaml.safe_load(data)
client = pymongo.MongoClient(yaml_reader['connection_url'])
db = client[yaml_reader['db']]
db_collection_User = db[yaml_reader['collection_User']]
db_collection_Order_History = db[yaml_reader['collection_Order_History']]
db_collection_cart_history = db[yaml_reader['collection_Cart_History']]

error_ = ""


def getError():
    return error_


@register_api.route('/register', methods=['GET'])
def register_page():
    return render_template("register.html")


@register_api.route('/register.html', methods=['GET'])
def register_page1():
    return render_template("register.html")
